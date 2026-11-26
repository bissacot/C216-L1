import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import URL


def database_url() -> URL:
    load_dotenv(Path(__file__).resolve().parents[3] / ".env")
    return URL.create(
        "postgresql+psycopg",
        username=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        host=os.getenv("POSTGRES_HOST", "127.0.0.1"),
        port=int(os.getenv("POSTGRES_PORT", "5433")),
        database=os.environ["POSTGRES_DB"],
    )
