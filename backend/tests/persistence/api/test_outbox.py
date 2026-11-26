import asyncio
import threading
from datetime import timedelta

from live_server import isolated_database
from sqlalchemy import create_engine, func, select, update
from sqlalchemy.orm import Session

from app.models import Category, Notification, Requester, Ticket
from app.models.enums import Channel, NotificationStatus
from app.repositories.outbox import claim_one, complete
from app.services.delivery.settings import Mode, Policy
from app.services.delivery.worker import process_one

EMAIL = Channel.EMAIL


def _database(pg_engine):
    engine = create_engine(
        isolated_database(pg_engine), connect_args={"options": "-c lock_timeout=2000"}
    )
    with Session(engine) as db, db.begin():
        ticket = Ticket(
            requester=Requester(name="Demo", email="demo@example.invalid"),
            category=Category(name="Exemplo"),
            title="Teste",
            description="Teste",
        )
        ticket.notifications = [Notification(channel=EMAIL, recipient="suporte")]
        db.add(ticket)
    return engine


def test_recovery_limits_backoff_and_stale_completion(pg_engine):
    engine = _database(pg_engine)
    policy = Policy(3, 10, 1, 60)
    try:
        assert claim_one(engine, EMAIL, Mode.DISABLED, policy) is None
        first = claim_one(engine, EMAIL, Mode.MOCK, policy)
        assert first and claim_one(engine, EMAIL, Mode.MOCK, policy) is None
        with engine.begin() as conn:
            conn.execute(
                update(Notification).values(lease_until=func.now() - timedelta(days=1))
            )
        assert claim_one(engine, EMAIL, Mode.MOCK, policy) is None
        for attempt in (1, 2, 3):
            with Session(engine) as db, db.begin():
                row = db.scalar(select(Notification))
                assert (
                    row.status == NotificationStatus.FAILED
                    and row.attempt_count == attempt
                )
                if attempt < 3:
                    assert (
                        row.next_attempt_at - row.last_attempt_at
                    ).total_seconds() >= 10 * 2 ** (attempt - 1)
                    assert claim_one(engine, EMAIL, Mode.MOCK, policy) is None
                    row.next_attempt_at = db.scalar(select(func.now())) - timedelta(
                        seconds=1
                    )
                else:
                    assert row.next_attempt_at is None
            current = claim_one(engine, EMAIL, Mode.MOCK, policy)
            if current:
                complete(engine, first, None, policy)
                complete(engine, current, "Falha de teste.", policy)
        assert current is None
    finally:
        engine.dispose()


def test_in_flight_send_renews_claim_without_db_lock(pg_engine):
    engine = _database(pg_engine)
    policy = Policy(3, 1, 0.1, 0.6)
    started, release = threading.Event(), threading.Event()

    class Paused:
        def send(self, message):
            started.set()
            assert release.wait(10)

    async def race():
        task = asyncio.create_task(
            process_one(engine, EMAIL, Mode.MOCK, Paused(), policy)
        )
        try:
            assert await asyncio.to_thread(started.wait, 5)
            with Session(engine) as db, db.begin():
                # NOWAIT falharia se a chamada de rede mantivesse o lock.
                row = db.scalar(select(Notification).with_for_update(nowait=True))
                original = row.lease_until
            await asyncio.sleep(policy.lease * 1.5)
            with Session(engine) as db:
                row = db.scalar(select(Notification))
                assert row.lease_until > original
                assert row.processing and row.attempt_count == 1
            assert (
                await asyncio.to_thread(claim_one, engine, EMAIL, Mode.MOCK, policy)
                is None
            )
        finally:
            release.set()
            await task

    try:
        asyncio.run(race())
        with Session(engine) as db:
            row = db.scalar(select(Notification))
            assert row.status == NotificationStatus.SENT and row.delivery_mode == "MOCK"
    finally:
        engine.dispose()


def test_retry_filters_and_ineligible_states(client, opened, session):
    notices = client.get(opened + "/notifications").json()
    id_ = notices[0]["id"]
    url = f"/notifications/{id_}/retry"
    assert client.post(url).status_code == 409
    assert client.post("/notifications/-999/retry").status_code == 404
    assert client.get("/notifications", params={"status": "BAD"}).status_code == 422
    page = client.get(
        "/notifications",
        params={
            "ticket_id": opened.split("/")[-1],
            "channel": notices[0]["channel"],
            "status": "PENDING",
            "page_size": 1,
        },
    ).json()
    assert page["total"] == 1 and page["items"] == [notices[0]]
    row = session.get(Notification, id_)
    row.attempt_count = row.cycle_attempt = 1
    row.last_attempt_at = session.scalar(select(func.now()))
    row.lease_until = row.last_attempt_at + timedelta(minutes=1)
    row.claim_token = "worker"
    session.flush()
    assert client.post(url).status_code == 409
    row.status = NotificationStatus.SENT
    row.lease_until = row.claim_token = None
    row.sent_at = row.last_attempt_at
    session.flush()
    assert client.post(url).status_code == 409


def test_worker_skips_locked_delivery_and_reserves_next(pg_engine):
    engine = _database(pg_engine)
    policy = Policy(3, 10, 1, 60)
    try:
        with Session(engine) as db, db.begin():
            first = db.scalar(select(Notification))
            first_id = first.id
            second = Notification(
                ticket_id=first.ticket_id, channel=EMAIL, recipient="plantao"
            )
            db.add(second)
            db.flush()
            second_id = second.id
        with Session(engine) as other_worker, other_worker.begin():
            other_worker.get(Notification, first_id, with_for_update=True)
            claim = claim_one(engine, EMAIL, Mode.MOCK, policy)
            assert claim.id == second_id
            assert claim_one(engine, EMAIL, Mode.MOCK, policy) is None
        assert claim_one(engine, EMAIL, Mode.MOCK, policy).id == first_id
    finally:
        engine.dispose()
