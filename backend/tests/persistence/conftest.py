import subprocess
import time
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import URL, create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from app.models import Category, Requester, Ticket

ALEMBIC_INI = Path(__file__).resolve().parents[2] / "alembic.ini"


@pytest.fixture(scope="session")
def migration_config():
    return Config(str(ALEMBIC_INI))


@pytest.fixture(scope="session")
def pg_engine(migration_config):
    # A URL é construída exclusivamente a partir do container criado por esta suíte.
    container = subprocess.check_output(
        [
            "docker",
            "run",
            "--detach",
            "--rm",
            "--tmpfs",
            "/var/lib/postgresql/data",
            "--publish",
            "127.0.0.1::5432",
            "--env",
            "POSTGRES_DB=helpdesk_test",
            "--env",
            "POSTGRES_PASSWORD=test_only",
            "postgres:16-alpine",
        ],
        text=True,
    ).strip()
    try:
        address = subprocess.check_output(
            ["docker", "port", container, "5432/tcp"], text=True
        )
        host, port = address.strip().rsplit(":", 1)
        engine = create_engine(
            URL.create(
                "postgresql+psycopg",
                username="postgres",
                password="test_only",
                host=host,
                port=int(port),
                database="helpdesk_test",
            ),
            connect_args={"connect_timeout": 2},
        )
        try:
            deadline = time.monotonic() + 60
            while True:
                try:
                    with engine.connect() as connection:
                        connection.execute(text("SELECT 1"))
                    break
                except OperationalError:
                    if time.monotonic() >= deadline:
                        raise
                    time.sleep(0.3)
            with engine.begin() as connection:
                migration_config.attributes["connection"] = connection
                command.upgrade(migration_config, "head")
            yield engine
        finally:
            migration_config.attributes.pop("connection", None)
            engine.dispose()
    finally:
        subprocess.run(
            ["docker", "stop", container], check=True, stdout=subprocess.DEVNULL
        )


@pytest.fixture
def session(pg_engine):
    with pg_engine.connect() as connection:
        transaction = connection.begin()
        try:
            with Session(
                connection, join_transaction_mode="create_savepoint"
            ) as session:
                yield session
        finally:
            transaction.rollback()


@pytest.fixture
def ticket(session):
    ticket = Ticket(
        title="Ajustar estação",
        description="Verificar estação de testes.",
        requester=Requester(name="Pessoa fictícia", email="demo@example.invalid"),
        category=Category(name="Teste"),
    )
    session.add(ticket)
    session.flush()
    return ticket
