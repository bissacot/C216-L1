from fastapi import APIRouter
from sqlalchemy import text

from app.database.session import ReadDatabase
from app.schemas.health import HealthResponse

router = APIRouter()


@router.get("/health", tags=["Sistema"])
def health() -> HealthResponse:
    return HealthResponse()


@router.get("/ready", tags=["Sistema"])
def ready(db: ReadDatabase) -> HealthResponse:
    db.execute(text("SELECT 1"))
    return HealthResponse()
