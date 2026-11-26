"""Fluxo HTTP em dois processos Uvicorn, ambos no PostgreSQL descartável da suíte."""

import os
import re
import subprocess
import sys
import time
from contextlib import contextmanager
from pathlib import Path
from uuid import uuid4

import httpx2
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine

BACKEND = Path(__file__).resolve().parents[3]


@contextmanager
def running_api(url, log, **delivery_env):
    env = {
        **os.environ,
        "POSTGRES_HOST": url.host,
        "POSTGRES_PORT": str(url.port),
        "POSTGRES_DB": url.database,
        "POSTGRES_USER": url.username,
        "POSTGRES_PASSWORD": url.password,
        "NOTIFY_EMAIL_RECIPIENT": "ti-email",
        "NOTIFY_TEAMS_RECIPIENT": "ti-teams",
        "EMAIL_MODE": "DISABLED",
        "TEAMS_MODE": "DISABLED",
        **delivery_env,
    }
    with log.open("wb") as output:
        process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "app.main:app",
                "--host",
                "127.0.0.1",
                "--port",
                "0",
                "--no-use-colors",
            ],
            cwd=BACKEND,
            env=env,
            stdout=output,
            stderr=subprocess.STDOUT,
        )
        try:
            deadline = time.monotonic() + 30
            while time.monotonic() < deadline:
                content = log.read_text(encoding="utf-8", errors="replace")
                match = re.search(
                    r"Uvicorn running on (http://127\.0\.0\.1:\d+)", content
                )
                if match:
                    break
                if process.poll() is not None:
                    raise RuntimeError(content)
                time.sleep(0.1)
            else:
                raise TimeoutError("API de teste não iniciou.")
            with httpx2.Client(
                base_url=match.group(1), trust_env=False, timeout=10
            ) as client:
                assert client.get("/health").json() == {"status": "ok"}
                yield client
        finally:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()


def isolated_database(pg_engine):
    # pg_engine pertence ao container em tmpfs criado pela fixture de persistência.
    db_name = "flow_" + uuid4().hex
    with pg_engine.connect().execution_options(
        isolation_level="AUTOCOMMIT"
    ) as connection:
        connection.exec_driver_sql(f"CREATE DATABASE {db_name}")
    url = pg_engine.url.set(database=db_name)
    engine = create_engine(url)
    try:
        with engine.begin() as connection:
            config = Config(str(BACKEND / "alembic.ini"))
            config.attributes["connection"] = connection
            command.upgrade(config, "head")
    finally:
        engine.dispose()

    return url
