from fastapi import APIRouter

from app.database.session import ReadDatabase
from app.repositories.dashboard import indicators
from app.schemas.dashboard import Dashboard

router = APIRouter(tags=["Indicadores"])


@router.get(
    "/dashboard", response_model=Dashboard, summary="Consultar indicadores gerais"
)
def dashboard(db: ReadDatabase):
    """Agrega chamados e entregas e retorna até cinco chamados recentes."""
    return indicators(db)
