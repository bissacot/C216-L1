import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routers.alunos import router as alunos_router
from backend.routers.geral import router as geral_router


def create_app() -> FastAPI:
    origins = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173,"
        "http://localhost:4173,http://127.0.0.1:4173",
    )
    allowed = [origin.strip() for origin in origins.split(",") if origin.strip()]
    if "*" in allowed:
        raise ValueError("CORS_ORIGINS exige origens explícitas.")

    app = FastAPI(title="C216 L1 API")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
        allow_headers=["Content-Type"],
    )
    app.include_router(geral_router)
    app.include_router(alunos_router)
    return app


app = create_app()
