"""Carga opcional de exemplos locais. Execute com python -m app.database.seed."""

from datetime import datetime, timezone

from sqlalchemy import create_engine, func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.database.config import database_url
from app.models import Category, Requester, Ticket
from app.models.enums import Priority, TicketStatus

CATEGORIES = (
    "ERP / Protheus",
    "Infraestrutura",
    "Redes e conectividade",
    "Hardware",
    "Software",
    "Acessos e permissões",
)
REQUESTERS = (
    ("Pessoa Demo Alfa", "alfa@example.invalid", "Laboratório fictício"),
    ("Pessoa Demo Beta", "beta@example.invalid", "Oficina fictícia"),
)


def seed_demo(session: Session) -> None:
    for name in CATEGORIES:
        session.execute(insert(Category).values(name=name).on_conflict_do_nothing())
    for name, email, department in REQUESTERS:
        session.execute(
            insert(Requester)
            .values(name=name, email=email, department=department)
            .on_conflict_do_nothing()
        )

    categories = dict(
        session.execute(
            select(Category.name, Category.id).where(Category.name.in_(CATEGORIES))
        ).all()
    )
    email_key = func.lower(func.btrim(Requester.email))
    requesters = dict(
        session.execute(
            select(email_key, Requester.id).where(
                email_key.in_([email for _, email, _ in REQUESTERS])
            )
        ).all()
    )

    # IDs negativos estáveis distinguem os exemplos dos IDs gerados pela sequência.
    examples = (
        (
            -1,
            "Instalar editor de texto",
            "Software",
            "alfa@example.invalid",
            Priority.LOW,
            TicketStatus.OPEN,
        ),
        (
            -2,
            "Revisar rota do laboratório",
            "Redes e conectividade",
            "beta@example.invalid",
            Priority.HIGH,
            TicketStatus.IN_PROGRESS,
        ),
        (
            -3,
            "Restaurar estação de treino",
            "Hardware",
            "alfa@example.invalid",
            Priority.CRITICAL,
            TicketStatus.RESOLVED,
        ),
        (
            -4,
            "Solicitar perfil de treinamento",
            "Acessos e permissões",
            "beta@example.invalid",
            Priority.MEDIUM,
            TicketStatus.CANCELLED,
        ),
    )
    for id_, title, category, email, priority, status in examples:
        resolved = status == TicketStatus.RESOLVED
        session.execute(
            insert(Ticket)
            .values(
                id=id_,
                title=title,
                description=f"Cenário fictício de demonstração: {title}.",
                requester_id=requesters[email],
                category_id=categories[category],
                priority=priority,
                status=status,
                resolution="Estação de treino restaurada." if resolved else None,
                resolved_at=datetime.now(timezone.utc) if resolved else None,
            )
            .on_conflict_do_nothing(index_elements=[Ticket.id])
        )


if __name__ == "__main__":
    engine = create_engine(database_url())
    with Session(engine) as session, session.begin():
        seed_demo(session)
    engine.dispose()
    print("Carga de demonstração concluída.")
