from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.repositories import aluno_repository
from backend.schemas.aluno import AlunoCreate, AlunoUpdate


def criar_aluno(db: Session, dados: AlunoCreate):
    return aluno_repository.criar_aluno(
        db,
        nome=dados.nome,
        email=dados.email,
        curso=dados.curso,
    )


def buscar_aluno(db: Session, aluno_id: int):
    aluno = aluno_repository.buscar_aluno(db, aluno_id)

    if aluno is None:
        raise HTTPException(
            status_code=404,
            detail="Aluno não encontrado",
        )

    return aluno


def listar_alunos(db: Session):
    return aluno_repository.listar_alunos(db)


def substituir_aluno(db: Session, aluno_id: int, dados: AlunoCreate):
    aluno = buscar_aluno(db, aluno_id)

    return aluno_repository.atualizar_aluno(db, aluno, dados.model_dump())


def atualizar_aluno(db: Session, aluno_id: int, dados: AlunoUpdate):
    aluno = buscar_aluno(db, aluno_id)

    return aluno_repository.atualizar_aluno(
        db,
        aluno,
        dados.model_dump(exclude_unset=True),
    )


def remover_aluno(db: Session, aluno_id: int):
    aluno = buscar_aluno(db, aluno_id)
    aluno_repository.remover_aluno(db, aluno)
