from typing import Annotated

from fastapi import APIRouter, Query, Request

from app.database.session import Database, ReadDatabase
from app.models.enums import Channel
from app.repositories import outbox
from app.schemas.common import Identifier, Page
from app.schemas.tickets import NotificationQuery, NotificationRead
from app.services.delivery.settings import Mode
from app.services.notifications import retry_failed

router = APIRouter(prefix="/notifications", tags=["Notificações"])


@router.get(
    "",
    response_model=Page[NotificationRead],
    summary="Pesquisar entregas por canal, status e chamado",
)
def list_notifications(db: ReadDatabase, query: Annotated[NotificationQuery, Query()]):
    return outbox.list_notifications(db, query)


@router.get("/channels", summary="Consultar modos públicos dos canais")
def channel_modes(request: Request) -> dict[Channel, Mode]:
    return request.app.state.channel_modes


@router.post(
    "/{id}/retry",
    response_model=NotificationRead,
    status_code=202,
    summary="Reagendar uma entrega com falha",
)
def retry(id: Identifier, db: Database):
    """Abre um novo ciclo de tentativas e preserva o contador acumulado."""
    return retry_failed(db, id)
