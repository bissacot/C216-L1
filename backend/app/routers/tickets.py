from typing import Annotated

from fastapi import APIRouter, Body, Header, Query

from app.database.session import Database, ReadDatabase
from app.models import Ticket
from app.repositories import tickets as repository
from app.schemas.common import Identifier, Page
from app.schemas.tickets import (
    HistoryRead,
    NotificationRead,
    StatusChange,
    TicketInput,
    TicketQuery,
    TicketRead,
)
from app.services import tickets
from app.services.catalog import require

router = APIRouter(prefix="/tickets", tags=["Chamados"])
Actor = Annotated[
    str | None,
    Header(
        alias="X-Changed-By",
        min_length=1,
        max_length=150,
        description="Autor declarado para o histórico.",
    ),
]


@router.post("", status_code=201, response_model=TicketRead, summary="Abrir chamado")
def open_ticket(data: TicketInput, db: Database, actor: Actor = None):
    """Registra a abertura e prepara uma entrega pendente para cada canal."""
    return tickets.open_ticket(db, data, actor)


@router.get("", response_model=Page[TicketRead], summary="Pesquisar chamados")
def list_tickets(db: ReadDatabase, query: Annotated[TicketQuery, Query()]):
    return repository.list_tickets(db, query)


@router.get("/{id}", response_model=TicketRead, summary="Consultar chamado")
def get_ticket(id: Identifier, db: ReadDatabase):
    return require(db, Ticket, id)


@router.put("/{id}", response_model=TicketRead, summary="Substituir dados operacionais")
def replace_ticket(
    id: Identifier, data: TicketInput, db: Database, actor: Actor = None
):
    return tickets.replace(db, id, data, actor)


@router.patch("/{id}/status", response_model=TicketRead, summary="Alterar status")
def change_status(
    id: Identifier,
    data: Annotated[
        StatusChange,
        Body(
            openapi_examples={
                "iniciar": {
                    "summary": "Iniciar atendimento",
                    "value": {"status": "IN_PROGRESS", "assignee": "Plantão A"},
                },
                "resolver": {
                    "summary": "Registrar solução",
                    "value": {"status": "RESOLVED", "resolution": "Cabo substituído."},
                },
                "cancelar": {
                    "summary": "Cancelar chamado",
                    "value": {"status": "CANCELLED"},
                },
            }
        ),
    ],
    db: Database,
    actor: Actor = None,
):
    """O atendimento exige um responsável. A resolução exige a descrição da solução."""
    return tickets.transition(db, id, data, actor)


@router.delete("/{id}", status_code=204, summary="Excluir chamado cancelado")
def delete_ticket(id: Identifier, db: Database):
    tickets.delete(db, id)


@router.get(
    "/{id}/history",
    response_model=list[HistoryRead],
    summary="Consultar histórico cronológico",
)
def history(id: Identifier, db: ReadDatabase):
    require(db, Ticket, id)
    return repository.history(db, id)


@router.get(
    "/{id}/notifications",
    response_model=list[NotificationRead],
    summary="Consultar entregas preparadas",
)
def notifications(id: Identifier, db: ReadDatabase):
    require(db, Ticket, id)
    return repository.notifications(db, id)
