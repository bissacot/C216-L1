from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import NotificationStatus, Priority, TicketStatus
from app.schemas.tickets import TicketRead


class CategoryCount(BaseModel):
    category_id: int
    name: str
    count: int


class Dashboard(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "total": 0,
                    "by_status": {
                        "OPEN": 0,
                        "IN_PROGRESS": 0,
                        "RESOLVED": 0,
                        "CANCELLED": 0,
                    },
                    "active_critical": 0,
                    "by_priority": {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0},
                    "by_category": [],
                    "average_resolution_seconds": None,
                    "recent_tickets": [],
                    "notifications": {"PENDING": 0, "SENT": 0, "FAILED": 0},
                }
            ]
        }
    )
    total: int
    by_status: dict[TicketStatus, int]
    active_critical: int
    by_priority: dict[Priority, int]
    by_category: list[CategoryCount]
    average_resolution_seconds: float | None = Field(
        description="Média em segundos. Nula sem resoluções datadas."
    )
    recent_tickets: list[TicketRead]
    notifications: dict[NotificationStatus, int]
