from typing import TypeVar

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models import Base, Category, Requester
from app.schemas.common import PageQuery

Record = TypeVar("Record", bound=Base)


def find(
    session: Session, model: type[Record], record_id: int, *, lock=False
) -> Record | None:
    statement = select(model).where(model.id == record_id)
    if lock:
        statement = statement.with_for_update()
    return session.scalar(statement)


def save(session: Session, record: Record) -> Record:
    session.add(record)
    session.flush()
    return record


def remove(session: Session, record: Base) -> None:
    session.delete(record)
    session.flush()


def paginate(session, statement, query, ordering):
    total = session.scalar(select(func.count()).select_from(statement.subquery()))
    rows = session.scalars(
        statement.order_by(*ordering)
        .offset((query.page - 1) * query.page_size)
        .limit(query.page_size)
    ).all()
    return {
        "items": rows,
        "total": total,
        "page": query.page,
        "page_size": query.page_size,
    }


def catalog_page(session, model, query: PageQuery):
    columns = (
        (Requester.name, Requester.email, Requester.department)
        if model is Requester
        else (Category.name, Category.description)
    )
    statement = select(model)
    if query.q:
        statement = statement.where(
            or_(*(column.icontains(query.q, autoescape=True) for column in columns))
        )
    return paginate(session, statement, query, [model.name, model.id])
