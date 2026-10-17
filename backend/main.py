from fastapi import FastAPI

from backend.routers.alunos import router as alunos_router
from backend.routers.geral import router as geral_router

app = FastAPI(title="C216 L1 API")

app.include_router(geral_router)
app.include_router(alunos_router)
