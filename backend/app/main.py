from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.database.config import cors_origins
from app.routers.catalog import router as catalog_router
from app.routers.dashboard import router as dashboard_router
from app.routers.health import router as health_router
from app.routers.notifications import router as notifications_router
from app.routers.tickets import router as tickets_router
from app.services.delivery.worker import lifespan
from app.services.errors import (
    ConfigurationError,
    Conflict,
    DomainError,
    InvalidInput,
    NotFound,
)

app = FastAPI(title="HelpDesk Hub", version="0.4.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins(),
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Content-Type", "X-Changed-By"],
)
app.include_router(health_router)
errors = {
    404: {"description": "Recurso inexistente"},
    409: {"description": "Conflito de integridade ou de estado"},
}
app.include_router(catalog_router, responses=errors)
app.include_router(tickets_router, responses=errors)
app.include_router(dashboard_router)
app.include_router(notifications_router, responses=errors)


@app.exception_handler(DomainError)
async def domain_error(request: Request, exc: DomainError):
    if isinstance(exc, InvalidInput):
        return JSONResponse(
            {"detail": [{"loc": ["body"], "msg": str(exc), "type": "value_error"}]},
            status_code=422,
        )
    codes = {NotFound: 404, Conflict: 409, ConfigurationError: 500}
    return JSONResponse({"detail": str(exc)}, status_code=codes[type(exc)])


@app.exception_handler(RequestValidationError)
async def invalid_input(request: Request, exc: RequestValidationError):
    issues = [{k: item[k] for k in ("loc", "msg", "type")} for item in exc.errors()]
    return JSONResponse({"detail": issues}, status_code=422)


@app.exception_handler(IntegrityError)
async def integrity_error(request: Request, exc: IntegrityError):
    messages = {
        "23505": "Já existe um registro com essa chave única.",
        "23503": "A operação conflita com um registro vinculado.",
    }
    message = messages.get(
        getattr(exc.orig, "sqlstate", None), "Conflito de integridade."
    )
    return JSONResponse({"detail": message}, status_code=409)


@app.exception_handler(SQLAlchemyError)
async def persistence_error(request: Request, exc: SQLAlchemyError):
    return JSONResponse({"detail": "Falha de persistência."}, status_code=500)
