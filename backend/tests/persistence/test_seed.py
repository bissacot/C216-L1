from sqlalchemy import func, select

from app.database.seed import seed_demo
from app.models import Category, Notification, Requester, Ticket
from app.models.enums import Priority, TicketStatus


def test_demo_is_idempotent_and_preserves_edits(session, ticket):
    seed_demo(session)
    records = list(session.scalars(select(Ticket).where(Ticket.id < 0)))
    assert {record.priority for record in records} == set(Priority)
    assert {record.status for record in records} == set(TicketStatus)
    assert all(
        record.resolved_at
        for record in records
        if record.status == TicketStatus.RESOLVED
    )
    records[0].title = "Título editado depois da carga"
    session.flush()
    seed_demo(session)
    session.expire_all()
    assert records[0].title == "Título editado depois da carga"
    assert ticket.title == "Ajustar estação"
    for model, expected in [
        (Category, 7),
        (Requester, 3),
        (Ticket, 5),
        (Notification, 0),
    ]:
        assert session.scalar(select(func.count()).select_from(model)) == expected
