from sqlalchemy import or_, select

from app.models import Notification, Ticket, TicketHistory
from app.repositories.records import paginate
from app.schemas.tickets import TicketQuery


def list_tickets(session, query: TicketQuery):
    statement = select(Ticket)
    for key in ("status", "priority", "category_id", "requester_id"):
        value = getattr(query, key)
        if value is not None:
            statement = statement.where(getattr(Ticket, key) == value)
    if query.assignee:
        statement = statement.where(
            Ticket.assignee.icontains(query.assignee, autoescape=True)
        )
    if query.opened_from:
        statement = statement.where(Ticket.opened_at >= query.opened_from)
    if query.opened_to:
        statement = statement.where(Ticket.opened_at <= query.opened_to)
    if query.q:
        statement = statement.where(
            or_(
                Ticket.title.icontains(query.q, autoescape=True),
                Ticket.description.icontains(query.q, autoescape=True),
            )
        )
    column = getattr(Ticket, query.sort_by)
    ordering = (
        [column.desc(), Ticket.id.desc()]
        if query.order == "desc"
        else [column.asc(), Ticket.id.asc()]
    )
    return paginate(session, statement, query, ordering)


def save_changes(session, events):
    session.add_all(events)
    session.flush()


def history(session, ticket_id):
    return session.scalars(
        select(TicketHistory)
        .where(TicketHistory.ticket_id == ticket_id)
        .order_by(TicketHistory.changed_at, TicketHistory.id)
    ).all()


def notifications(session, ticket_id):
    return session.scalars(
        select(Notification)
        .where(Notification.ticket_id == ticket_id)
        .order_by(Notification.id)
    ).all()
