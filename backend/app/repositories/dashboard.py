from sqlalchemy import extract, func, select

from app.models import Category, Notification, Ticket
from app.models.enums import NotificationStatus, Priority, TicketStatus


def indicators(session):
    by_status = dict.fromkeys(TicketStatus, 0)
    by_priority = dict.fromkeys(Priority, 0)
    active_critical = 0
    counts = select(Ticket.status, Ticket.priority, func.count()).group_by(
        Ticket.status, Ticket.priority
    )
    for status, priority, count in session.execute(counts):
        by_status[status] += count
        by_priority[priority] += count
        if priority == Priority.CRITICAL and status in (
            TicketStatus.OPEN,
            TicketStatus.IN_PROGRESS,
        ):
            active_critical += count
    categories = (
        select(
            Category.id.label("category_id"),
            Category.name,
            func.count(Ticket.id).label("count"),
        )
        .outerjoin(Ticket)
        .group_by(Category.id)
        .order_by(Category.name, Category.id)
    )
    mean_seconds = select(
        func.avg(extract("epoch", Ticket.resolved_at - Ticket.opened_at))
    ).where(Ticket.status == TicketStatus.RESOLVED)
    notifications = dict.fromkeys(NotificationStatus, 0)
    notifications.update(
        session.execute(
            select(Notification.status, func.count()).group_by(Notification.status)
        ).all()
    )
    recent = select(Ticket).order_by(Ticket.opened_at.desc(), Ticket.id.desc()).limit(5)
    return {
        "total": sum(by_status.values()),
        "by_status": by_status,
        "by_priority": by_priority,
        "active_critical": active_critical,
        "by_category": session.execute(categories).mappings().all(),
        "average_resolution_seconds": session.scalar(mean_seconds),
        "recent_tickets": session.scalars(recent).all(),
        "notifications": notifications,
    }
