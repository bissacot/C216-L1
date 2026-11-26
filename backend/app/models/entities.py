from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum,
    FetchedValue,
    ForeignKey,
    Index,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.enums import Channel, NotificationStatus, Priority, TicketStatus


class UpdatedAt:
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        server_onupdate=FetchedValue(),
    )


class Requester(UpdatedAt, Base):
    __tablename__ = "requesters"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150))
    email: Mapped[str] = mapped_column(String(254))
    department: Mapped[str | None] = mapped_column(String(150))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    tickets: Mapped[list[Ticket]] = relationship(
        back_populates="requester", passive_deletes="all"
    )

    __table_args__ = (
        CheckConstraint("btrim(name) <> ''", name="ck_requesters_name"),
        CheckConstraint("btrim(email) <> ''", name="ck_requesters_email"),
        Index("uq_requesters_email", func.lower(func.btrim(email)), unique=True),
    )


class Category(UpdatedAt, Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    description: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    tickets: Mapped[list[Ticket]] = relationship(
        back_populates="category", passive_deletes="all"
    )

    __table_args__ = (CheckConstraint("btrim(name) <> ''", name="ck_categories_name"),)


class Ticket(UpdatedAt, Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text)
    requester_id: Mapped[int] = mapped_column(
        ForeignKey("requesters.id", ondelete="RESTRICT"), index=True
    )
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="RESTRICT"), index=True
    )
    priority: Mapped[Priority] = mapped_column(
        Enum(Priority, name="ticket_priority"), server_default=Priority.MEDIUM.value
    )
    status: Mapped[TicketStatus] = mapped_column(
        Enum(TicketStatus, name="ticket_status"), server_default=TicketStatus.OPEN.value
    )
    assignee: Mapped[str | None] = mapped_column(String(150))
    resolution: Mapped[str | None] = mapped_column(Text)
    opened_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    requester: Mapped[Requester] = relationship(back_populates="tickets")
    category: Mapped[Category] = relationship(back_populates="tickets")
    history: Mapped[list[TicketHistory]] = relationship(
        back_populates="ticket", cascade="all, delete", passive_deletes=True
    )
    notifications: Mapped[list[Notification]] = relationship(
        back_populates="ticket", cascade="all, delete", passive_deletes=True
    )

    __table_args__ = (
        CheckConstraint("btrim(title) <> ''", name="ck_tickets_title"),
        CheckConstraint("btrim(description) <> ''", name="ck_tickets_description"),
    )


class TicketHistory(Base):
    __tablename__ = "ticket_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.id", ondelete="CASCADE"))
    field_name: Mapped[str] = mapped_column(String(100))
    old_value: Mapped[str | None] = mapped_column(Text)
    new_value: Mapped[str | None] = mapped_column(Text)
    changed_by: Mapped[str | None] = mapped_column(String(150))
    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    ticket: Mapped[Ticket] = relationship(back_populates="history")

    __table_args__ = (
        CheckConstraint("btrim(field_name) <> ''", name="ck_history_field_name"),
        Index("ix_history_ticket_changed", "ticket_id", "changed_at"),
    )


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(primary_key=True)
    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.id", ondelete="CASCADE"))
    channel: Mapped[Channel] = mapped_column(Enum(Channel, name="notification_channel"))
    status: Mapped[NotificationStatus] = mapped_column(
        Enum(NotificationStatus, name="notification_status"),
        server_default=NotificationStatus.PENDING.value,
    )
    recipient: Mapped[str] = mapped_column(String(120))
    attempt_count: Mapped[int] = mapped_column(server_default="0")
    last_error: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    last_attempt_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    ticket: Mapped[Ticket] = relationship(back_populates="notifications")

    delivery_mode: Mapped[str | None] = mapped_column(String(4))
    claim_token: Mapped[str | None] = mapped_column(String(32))
    lease_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    next_attempt_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    cycle_attempt: Mapped[int] = mapped_column(server_default="0")

    @property
    def processing(self) -> bool:
        return self.claim_token is not None

    __table_args__ = (
        CheckConstraint("delivery_mode IN ('LIVE', 'MOCK')", name="ck_delivery_mode"),
        CheckConstraint(
            "cycle_attempt BETWEEN 0 AND attempt_count", name="ck_delivery_cycle"
        ),
        CheckConstraint(
            "(claim_token IS NULL) = (lease_until IS NULL) AND "
            "(claim_token IS NULL OR status = 'PENDING')",
            name="ck_delivery_lease",
        ),
        Index("ix_delivery_due", "channel", "status", "next_attempt_at", "id"),
        UniqueConstraint(
            "ticket_id", "channel", "recipient", name="uq_notifications_destination"
        ),
        CheckConstraint(
            "recipient ~ '^[a-z][a-z0-9._-]*$'", name="ck_notifications_alias"
        ),
        CheckConstraint(
            "(attempt_count = 0 AND last_attempt_at IS NULL) OR "
            "(attempt_count > 0 AND last_attempt_at IS NOT NULL)",
            name="ck_notifications_attempt",
        ),
        CheckConstraint(
            "status = 'PENDING' OR attempt_count > 0",
            name="ck_notifications_attempted_status",
        ),
        CheckConstraint(
            "(status = 'SENT') = (sent_at IS NOT NULL)", name="ck_notifications_sent"
        ),
        Index("ix_notifications_status_last_attempt", "status", "last_attempt_at"),
    )
