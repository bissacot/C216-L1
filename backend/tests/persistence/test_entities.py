from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import delete, func, select, update
from sqlalchemy.exc import DataError, IntegrityError

from app.models import Category, Notification, Requester, Ticket, TicketHistory
from app.models.enums import Channel, NotificationStatus, Priority, TicketStatus


def test_graph_and_defaults(session, ticket):
    history = TicketHistory(ticket=ticket, field_name="assignee", new_value="Plantão")
    notice = Notification(ticket=ticket, channel=Channel.EMAIL, recipient="solicitante")
    session.add_all([history, notice])
    session.flush()
    session.expire_all()
    assert ticket.requester.tickets == [ticket]
    assert ticket.category.tickets == [ticket]
    assert ticket.history == [history] and history.ticket is ticket
    assert ticket.notifications == [notice] and notice.ticket is ticket
    assert ticket.priority == Priority.MEDIUM and ticket.status == TicketStatus.OPEN
    assert ticket.assignee is ticket.resolution is ticket.resolved_at is None
    assert history.old_value is history.changed_by is None
    assert notice.status == NotificationStatus.PENDING and notice.attempt_count == 0
    assert notice.sent_at is notice.last_attempt_at is notice.last_error is None
    for instant in (
        ticket.requester.created_at,
        ticket.category.created_at,
        ticket.opened_at,
        ticket.updated_at,
        history.changed_at,
        notice.created_at,
    ):
        assert instant.utcoffset() == timedelta(0)


def test_timestamp_converts_offset_to_utc(session, ticket):
    instant = datetime(2025, 5, 1, 9, tzinfo=timezone(timedelta(hours=-3)))
    ticket.resolved_at = instant
    session.flush()
    session.refresh(ticket)
    assert ticket.resolved_at == instant.astimezone(timezone.utc)
    assert ticket.resolved_at.hour == 12


@pytest.mark.parametrize(
    ("entity", "field"),
    [
        (Requester, "department"),
        (Category, "description"),
        (Ticket, "description"),
    ],
)
def test_database_updates_timestamp(session, ticket, entity, field):
    row = {Requester: ticket.requester, Category: ticket.category, Ticket: ticket}[
        entity
    ]
    original = row.updated_at
    session.execute(
        update(entity.__table__)
        .where(entity.id == row.id)
        .values({field: "Atualizado"})
    )
    session.refresh(row)
    assert row.updated_at > original


@pytest.mark.parametrize(
    ("entity", "field"),
    [
        (Requester, "name"),
        (Requester, "email"),
        (Category, "name"),
        (Ticket, "title"),
        (Ticket, "description"),
        (Ticket, "requester_id"),
        (Ticket, "category_id"),
        (Ticket, "priority"),
        (Ticket, "status"),
        (TicketHistory, "ticket_id"),
        (TicketHistory, "field_name"),
        (Notification, "ticket_id"),
        (Notification, "channel"),
        (Notification, "recipient"),
        (Notification, "status"),
        (Notification, "attempt_count"),
    ],
)
def test_database_requires_fields(session, ticket, entity, field):
    history = TicketHistory(ticket=ticket, field_name="priority")
    notice = Notification(ticket=ticket, channel=Channel.TEAMS, recipient="suporte")
    session.add_all([history, notice])
    session.flush()
    with pytest.raises(IntegrityError) as error:
        session.execute(update(entity.__table__).values({field: None}))
    assert error.value.orig.sqlstate == "23502"


@pytest.mark.parametrize(
    ("entity", "field"),
    [
        (Requester, "name"),
        (Requester, "email"),
        (Category, "name"),
        (Ticket, "title"),
        (Ticket, "description"),
        (TicketHistory, "field_name"),
    ],
)
def test_required_text_rejects_blanks(session, ticket, entity, field):
    session.add(TicketHistory(ticket=ticket, field_name="status"))
    session.flush()
    with pytest.raises(IntegrityError) as error:
        session.execute(update(entity.__table__).values({field: "   "}))
    assert error.value.orig.sqlstate == "23514"


@pytest.mark.parametrize("entity", [Requester, Category])
def test_unique_natural_keys(session, ticket, entity):
    duplicate = (
        Requester(name="Outro", email=" DEMO@EXAMPLE.INVALID ")
        if entity is Requester
        else Category(name=ticket.category.name)
    )
    session.add(duplicate)
    with pytest.raises(IntegrityError) as error:
        session.flush()
    assert error.value.orig.sqlstate == "23505"


@pytest.mark.parametrize(
    ("entity", "field"),
    [
        (Ticket, "category_id"),
        (Ticket, "requester_id"),
        (TicketHistory, "ticket_id"),
        (Notification, "ticket_id"),
    ],
)
def test_foreign_keys(session, ticket, entity, field):
    session.add_all(
        [
            TicketHistory(ticket=ticket, field_name="priority"),
            Notification(ticket=ticket, channel=Channel.EMAIL, recipient="suporte"),
        ]
    )
    session.flush()
    with pytest.raises(IntegrityError) as error:
        session.execute(update(entity.__table__).values({field: -900}))
    assert error.value.orig.sqlstate == "23503"


@pytest.mark.parametrize(
    ("entity", "field"),
    [
        (Ticket, "priority"),
        (Ticket, "status"),
        (Notification, "channel"),
        (Notification, "status"),
    ],
)
def test_postgres_rejects_unknown_enum(session, ticket, entity, field):
    session.add(Notification(ticket=ticket, channel=Channel.EMAIL, recipient="suporte"))
    session.flush()
    with pytest.raises(DataError) as error:
        session.execute(update(entity.__table__).values({field: "INVALID"}))
    assert error.value.orig.sqlstate == "22P02"


@pytest.mark.parametrize("relation", ["requester", "category"])
def test_linked_parent_cannot_be_deleted(session, ticket, relation):
    parent = getattr(ticket, relation)
    assert parent.tickets == [ticket]
    session.delete(parent)
    with pytest.raises(IntegrityError) as error:
        session.flush()
    assert error.value.orig.sqlstate == "23503"


def test_database_cascades_only_children_of_deleted_ticket(session, ticket):
    other = Ticket(
        requester=ticket.requester,
        category=ticket.category,
        title="Outro",
        description="Teste",
    )
    session.add(other)
    for record in (ticket, other):
        session.add_all(
            [
                TicketHistory(ticket=record, field_name="status"),
                Notification(ticket=record, channel=Channel.EMAIL, recipient="suporte"),
            ]
        )
    session.flush()
    session.execute(delete(Ticket.__table__).where(Ticket.id == ticket.id))
    for child in (TicketHistory, Notification):
        assert session.scalars(select(child.ticket_id)).all() == [other.id]
    for parent in (Requester, Category):
        assert session.scalar(select(func.count()).select_from(parent)) == 1
