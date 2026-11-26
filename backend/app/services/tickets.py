import os
import re
from datetime import datetime, timezone
from enum import Enum

from app.models import Category, Notification, Requester, Ticket, TicketHistory
from app.models.enums import Channel, TicketStatus
from app.repositories import records
from app.repositories import tickets as repository
from app.schemas.tickets import StatusChange, TicketInput
from app.services.catalog import require
from app.services.errors import ConfigurationError, Conflict, InvalidInput

TRANSITIONS = {
    TicketStatus.OPEN: {TicketStatus.IN_PROGRESS, TicketStatus.CANCELLED},
    TicketStatus.IN_PROGRESS: {TicketStatus.RESOLVED, TicketStatus.CANCELLED},
    TicketStatus.RESOLVED: set(),
    TicketStatus.CANCELLED: set(),
}


def _references(session, data):
    require(session, Requester, data.requester_id)
    require(session, Category, data.category_id)


def _pending(channel: Channel) -> Notification:
    recipient = os.getenv(f"NOTIFY_{channel.value}_RECIPIENT", "suporte-ti")
    if not re.fullmatch(r"[a-z][a-z0-9._-]{0,119}", recipient):
        raise ConfigurationError("Configuração de destinatário inválida.")
    return Notification(channel=channel, recipient=recipient)


def open_ticket(session, data: TicketInput, actor):
    _references(session, data)
    ticket = Ticket(**data.model_dump(), status=TicketStatus.OPEN)
    ticket.history = [
        TicketHistory(
            field_name="status", old_value=None, new_value="OPEN", changed_by=actor
        )
    ]
    ticket.notifications = [_pending(Channel.EMAIL), _pending(Channel.TEAMS)]
    return records.save(session, ticket)


def _history_value(value):
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value) if value is not None else None


def _apply(session, ticket, changes, actor):
    events = []
    changed_at = datetime.now(timezone.utc)
    for field, value in changes.items():
        previous = getattr(ticket, field)
        if previous != value:
            events.append(
                TicketHistory(
                    ticket_id=ticket.id,
                    field_name=field,
                    old_value=_history_value(previous),
                    new_value=_history_value(value),
                    changed_by=actor,
                    changed_at=changed_at,
                )
            )
            setattr(ticket, field, value)
    repository.save_changes(session, events)
    return ticket


def replace(session, ticket_id, data: TicketInput, actor):
    ticket = require(session, Ticket, ticket_id, lock=True)
    if not TRANSITIONS[ticket.status]:
        raise Conflict("Chamado encerrado não permite edição.")
    if ticket.status == TicketStatus.IN_PROGRESS and not data.assignee:
        raise InvalidInput("O chamado em atendimento precisa de um responsável.")
    _references(session, data)
    return _apply(session, ticket, data.model_dump(), actor)


def transition_changes(ticket, data: StatusChange):
    if data.status not in TRANSITIONS[ticket.status]:
        raise Conflict("Transição de status não permitida.")
    changes = {"status": data.status}
    if data.status == TicketStatus.IN_PROGRESS:
        assignee = data.assignee or ticket.assignee
        if not assignee:
            raise InvalidInput("Informe o responsável para iniciar o atendimento.")
        changes["assignee"] = assignee
    elif data.assignee is not None:
        raise InvalidInput("Informe o responsável ao iniciar o atendimento.")
    if data.status == TicketStatus.RESOLVED:
        if not data.resolution:
            raise InvalidInput("Informe a solução para resolver o chamado.")
        changes.update(
            resolution=data.resolution, resolved_at=datetime.now(timezone.utc)
        )
    elif data.resolution is not None:
        raise InvalidInput("Informe a solução ao resolver o chamado.")
    return changes


def transition(session, ticket_id, data, actor):
    ticket = require(session, Ticket, ticket_id, lock=True)
    return _apply(session, ticket, transition_changes(ticket, data), actor)


def delete(session, ticket_id):
    ticket = require(session, Ticket, ticket_id, lock=True)
    if ticket.status != TicketStatus.CANCELLED:
        raise Conflict("Somente chamados cancelados podem ser excluídos.")
    records.remove(session, ticket)
