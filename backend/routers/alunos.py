from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database.session import get_db
from backend.schemas.aluno import Aluno, AlunoCreate, AlunoUpdate
from backend.services import aluno_service

router = APIRouter(prefix="/alunos", tags=["Alunos"])

DbSession = Annotated[Session, Depends(get_db)]


@router.post("/", response_model=Aluno, status_code=201)
def criar_aluno(
    dados: AlunoCreate,
    db: DbSession,
):
    return aluno_service.criar_aluno(db, dados)


@router.get("/", response_model=list[Aluno])
def listar_alunos(db: DbSession):
    return aluno_service.listar_alunos(db)


@router.get("/{aluno_id}", response_model=Aluno)
def buscar_aluno(
    aluno_id: int,
    db: DbSession,
):
    return aluno_service.buscar_aluno(db, aluno_id)


@router.put("/{aluno_id}", response_model=Aluno)
def substituir_aluno(
    aluno_id: int,
    dados: AlunoCreate,
    db: DbSession,
):
    return aluno_service.substituir_aluno(db, aluno_id, dados)


@router.patch("/{aluno_id}", response_model=Aluno)
def atualizar_aluno(
    aluno_id: int,
    dados: AlunoUpdate,
    db: DbSession,
):
    return aluno_service.atualizar_aluno(db, aluno_id, dados)


@router.delete("/{aluno_id}", status_code=204)
def remover_aluno(
    aluno_id: int,
    db: DbSession,
):
    aluno_service.remover_aluno(db, aluno_id)
