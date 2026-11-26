from datetime import datetime, timezone

import pytest
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from app.models import Notification, Ticket
from app.models.enums import Channel, NotificationStatus


def test_retry_updates_same_delivery(session, ticket):
    notice = Notification(ticket=ticket, channel=Channel.TEAMS, recipient="suporte")
    session.add(notice)
    session.flush()
    notice.status = NotificationStatus.FAILED
    notice.last_attempt_at = datetime.now(timezone.utc)
    notice.attempt_count += 1
    notice.last_error = "Serviço temporariamente indisponível."
    session.flush()
    session.refresh(notice)
    assert notice.sent_at is None and notice.attempt_count == 1
    notice.status = NotificationStatus.SENT
    notice.last_attempt_at = notice.sent_at = datetime.now(timezone.utc)
    notice.attempt_count += 1
    notice.last_error = None
    session.flush()
    session.refresh(notice)
    assert notice.status == NotificationStatus.SENT and notice.attempt_count == 2
    assert session.scalar(select(func.count()).select_from(Notification)) == 1


def test_unique_destination_per_ticket_and_channel(session, ticket):
    other = Ticket(
        requester=ticket.requester,
        category=ticket.category,
        title="Outro",
        description="Teste",
    )
    for record, channel, recipient in [
        (ticket, Channel.EMAIL, "suporte"),
        (ticket, Channel.TEAMS, "suporte"),
        (ticket, Channel.EMAIL, "plantao"),
        (other, Channel.EMAIL, "suporte"),
    ]:
        session.add(Notification(ticket=record, channel=channel, recipient=recipient))
    session.flush()
    session.add(Notification(ticket=ticket, channel=Channel.EMAIL, recipient="suporte"))
    with pytest.raises(IntegrityError) as error:
        session.flush()
    assert error.value.orig.sqlstate == "23505"


@pytest.mark.parametrize(
    "invalid",
    [
        {"attempt_count": -1},
        {"attempt_count": 1},
        {"last_attempt_at": datetime.now(timezone.utc)},
        {"status": NotificationStatus.FAILED},
        {
            "status": NotificationStatus.SENT,
            "attempt_count": 1,
            "last_attempt_at": datetime.now(timezone.utc),
        },
        {"sent_at": datetime.now(timezone.utc)},
        {"recipient": "https://example.invalid/private"},
    ],
)
def test_rejects_inconsistent_delivery(session, ticket, invalid):
    values = {"channel": Channel.EMAIL, "recipient": "suporte", **invalid}
    session.add(Notification(ticket=ticket, **values))
    with pytest.raises(IntegrityError) as error:
        session.flush()
    assert error.value.orig.sqlstate == "23514"
