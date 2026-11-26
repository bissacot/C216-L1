from datetime import datetime
from typing import Annotated, Literal

from pydantic import AwareDatetime, ConfigDict, Field, model_validator

from app.models.enums import Channel, NotificationStatus, Priority, TicketStatus
from app.schemas.common import Identifier, Input, Name, Output, PageQuery, TextValue


class TicketInput(Input):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "title": "Monitor sem imagem",
                    "description": "Verificar o cabo.",
                    "requester_id": 1,
                    "category_id": 1,
                    "priority": "HIGH",
                }
            ]
        }
    )
    title: Annotated[
        str, Field(min_length=1, max_length=200, examples=["Monitor sem imagem"])
    ]
    description: TextValue = Field(examples=["O monitor não liga após reiniciar."])
    requester_id: Identifier = Field(examples=[1])
    category_id: Identifier = Field(examples=[1])
    priority: Priority = Priority.MEDIUM
    assignee: Name | None = None


class StatusChange(Input):
    status: TicketStatus = Field(examples=["IN_PROGRESS"])
    assignee: Name | None = Field(None, examples=["Plantão A"])
    resolution: TextValue | None = None


class TicketQuery(PageQuery):
    status: TicketStatus | None = None
    priority: Priority | None = None
    category_id: Identifier | None = None
    requester_id: Identifier | None = None
    assignee: Name | None = None
    opened_from: AwareDatetime | None = Field(
        None, description="Início inclusivo, com fuso horário."
    )
    opened_to: AwareDatetime | None = Field(
        None, description="Fim inclusivo, com fuso horário."
    )
    sort_by: Literal["opened_at", "updated_at", "id", "title", "priority", "status"] = (
        "opened_at"
    )
    order: Literal["asc", "desc"] = "desc"

    @model_validator(mode="after")
    def ordered_period(self):
        if self.opened_from and self.opened_to and self.opened_from > self.opened_to:
            raise ValueError("Período de abertura invertido.")
        return self


class TicketRead(Output):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "id": 7,
                    "title": "Monitor sem imagem",
                    "description": "Verificar o cabo.",
                    "requester_id": 1,
                    "category_id": 1,
                    "priority": "HIGH",
                    "status": "OPEN",
                    "assignee": None,
                    "resolution": None,
                    "resolved_at": None,
                    "opened_at": "2026-01-15T12:00:00Z",
                    "updated_at": "2026-01-15T12:00:00Z",
                }
            ]
        }
    )
    id: int = Field(examples=[1])
    title: str = Field(examples=["Monitor sem imagem"])
    description: str
    requester_id: int
    category_id: int
    priority: Priority
    status: TicketStatus
    assignee: str | None
    resolution: str | None
    opened_at: datetime
    updated_at: datetime
    resolved_at: datetime | None


class HistoryRead(Output):
    id: int
    ticket_id: int
    field_name: str = Field(examples=["status"])
    old_value: str | None = Field(examples=["OPEN"])
    new_value: str | None = Field(examples=["IN_PROGRESS"])
    changed_by: str | None
    changed_at: datetime


class NotificationRead(Output):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "id": 1,
                    "ticket_id": 7,
                    "channel": "EMAIL",
                    "status": "PENDING",
                    "recipient": "suporte-ti",
                    "attempt_count": 0,
                    "last_error": None,
                    "created_at": "2026-01-15T12:00:00Z",
                    "last_attempt_at": None,
                    "sent_at": None,
                }
            ]
        }
    )
    id: int
    ticket_id: int
    channel: Channel
    status: NotificationStatus
    recipient: str = Field(examples=["suporte-ti"])
    attempt_count: int
    last_error: str | None
    created_at: datetime
    last_attempt_at: datetime | None
    sent_at: datetime | None
