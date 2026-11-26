from collections.abc import Iterator
from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session

from app.database.config import database_url


@lru_cache
def get_engine() -> Engine:
    return create_engine(database_url(), pool_pre_ping=True)


def get_session() -> Iterator[Session]:
    with Session(get_engine(), expire_on_commit=False) as session, session.begin():
        yield session


# Finaliza a transação antes de enviar a resposta HTTP, inclusive em erro de commit.
Database = Annotated[Session, Depends(get_session, scope="function")]


def get_read_session() -> Iterator[Session]:
    # A contagem e os itens de uma página (ou painel) usam o mesmo snapshot.
    bind = get_engine().execution_options(isolation_level="REPEATABLE READ")
    with Session(bind) as session:
        yield session


ReadDatabase = Annotated[Session, Depends(get_read_session, scope="function")]
