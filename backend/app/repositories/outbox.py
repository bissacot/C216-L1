from dataclasses import dataclass
from datetime import timedelta
from uuid import uuid4

from sqlalchemy import and_, func, or_, select, update
from sqlalchemy.orm import Session

from app.models import Notification
from app.models.enums import NotificationStatus
from app.repositories.records import paginate
from app.services.delivery.messages import TicketMessage
from app.services.delivery.settings import Mode, Policy


@dataclass(frozen=True)
class Claim:
    id: int
    token: str
    message: TicketMessage


def list_notifications(db, query):
    statement = select(Notification)
    for key in ("channel", "status", "ticket_id"):
        value = getattr(query, key)
        if value is not None:
            statement = statement.where(getattr(Notification, key) == value)
    return paginate(db, statement, query, [Notification.id.desc()])


def _fail(row, now, error, policy):
    row.status = NotificationStatus.FAILED
    row.last_error = error
    row.claim_token = row.lease_until = None
    row.next_attempt_at = None
    if row.cycle_attempt < policy.max_attempts:
        delay = min(86400, policy.backoff * 2 ** (row.cycle_attempt - 1))
        row.next_attempt_at = now + timedelta(seconds=delay)


def claim_one(engine, channel, mode: Mode, policy: Policy) -> Claim | None:
    if mode == Mode.DISABLED:
        return None
    with Session(engine) as db, db.begin():
        now = db.scalar(select(func.clock_timestamp()))
        ready = or_(
            and_(
                Notification.status == NotificationStatus.PENDING,
                or_(
                    Notification.claim_token.is_(None), Notification.lease_until <= now
                ),
            ),
            and_(
                Notification.status == NotificationStatus.FAILED,
                Notification.next_attempt_at <= now,
            ),
        )
        row = db.scalar(
            select(Notification)
            .where(Notification.channel == channel, ready)
            .order_by(Notification.id)
            .limit(1)
            .with_for_update(skip_locked=True)
        )
        if row is None:
            return None
        if row.claim_token is not None:
            _fail(row, now, "Tentativa interrompida; resultado desconhecido.", policy)
            return None
        if row.cycle_attempt >= policy.max_attempts:
            row.status = NotificationStatus.FAILED
            row.next_attempt_at = None
            return None
        row.status = NotificationStatus.PENDING
        row.delivery_mode = mode.value
        row.cycle_attempt += 1
        row.attempt_count += 1
        row.last_attempt_at = now
        row.next_attempt_at = None
        row.claim_token = uuid4().hex
        row.lease_until = now + timedelta(seconds=policy.lease)
        ticket = row.ticket
        message = TicketMessage(
            ticket.id,
            ticket.title,
            ticket.description,
            ticket.requester.name,
            ticket.requester.department,
            ticket.category.name,
            ticket.priority.value,
            ticket.status.value,
            ticket.opened_at.isoformat(),
        )
        return Claim(row.id, row.claim_token, message)


def renew(engine, claim, policy):
    with engine.begin() as conn:
        conn.execute(
            update(Notification)
            .where(Notification.id == claim.id, Notification.claim_token == claim.token)
            .values(
                lease_until=func.clock_timestamp() + timedelta(seconds=policy.lease)
            )
        )


def complete(engine, claim, error, policy):
    with Session(engine) as db, db.begin():
        row = db.scalar(
            select(Notification)
            .where(Notification.id == claim.id, Notification.claim_token == claim.token)
            .with_for_update()
        )
        if row is None:
            return
        now = db.scalar(select(func.clock_timestamp()))
        if error is not None:
            _fail(row, now, error, policy)
        else:
            row.status = NotificationStatus.SENT
            row.sent_at = now
            row.last_error = row.claim_token = row.lease_until = None
