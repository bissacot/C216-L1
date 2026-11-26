"""Modelos de domínio mapeados pelo SQLAlchemy."""

from app.database.base import Base
from app.models.entities import Category, Notification, Requester, Ticket, TicketHistory

__all__ = ["Base", "Category", "Notification", "Requester", "Ticket", "TicketHistory"]
