import os
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker, Session

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/alunos_db"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

app = FastAPI(title="Gerenciador de Alunos com PostgreSQL")


class AlunoDB(Base):
    __tablename__ = "alunos"

    id = Column(String, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    email = Column(String, nullable=False)
    curso = Column(String, nullable=False)
    matricula = Column(Integer, nullable=False)


class AlunoCreate(BaseModel):
    nome: str
    email: EmailStr
    curso: str


class AlunoUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[EmailStr] = None
    curso: Optional[str] = None


Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def aluno_to_dict(aluno: AlunoDB):
    return {
        "id": aluno.id,
        "nome": aluno.nome,
        "email": aluno.email,
        "curso": aluno.curso,
        "matricula": aluno.matricula,
    }


def gerar_matricula(db: Session, curso: str):
    ultimo = (
        db.query(AlunoDB)
        .filter(AlunoDB.curso == curso)
        .order_by(AlunoDB.matricula.desc())
        .first()
    )

    if ultimo is None:
        return 1

    return ultimo.matricula + 1


@app.get("/")
def home():
    return {"mensagem": "API funcionando com PostgreSQL!"}


@app.post("/api/v1/alunos/")
def criar_aluno(aluno: AlunoCreate, db: Session = Depends(get_db)):
    curso = aluno.curso.upper()

    if curso not in ["GES", "GEC"]:
        raise HTTPException(status_code=400, detail="Curso deve ser GES ou GEC")

    matricula = gerar_matricula(db, curso)
    aluno_id = f"{curso}{matricula}"

    novo_aluno = AlunoDB(
        id=aluno_id,
        nome=aluno.nome,
        email=aluno.email,
        curso=curso,
        matricula=matricula,
    )

    db.add(novo_aluno)
    db.commit()
    db.refresh(novo_aluno)

    return aluno_to_dict(novo_aluno)


@app.get("/api/v1/alunos/")
def listar_alunos(db: Session = Depends(get_db)):
    alunos = db.query(AlunoDB).order_by(AlunoDB.id).all()
    return [aluno_to_dict(aluno) for aluno in alunos]


@app.get("/api/v1/alunos/{aluno_id}")
def buscar_aluno(aluno_id: str, db: Session = Depends(get_db)):
    aluno = db.query(AlunoDB).filter(AlunoDB.id == aluno_id.upper()).first()

    if aluno is None:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")

    return aluno_to_dict(aluno)


@app.patch("/api/v1/alunos/{aluno_id}")
def atualizar_aluno(
    aluno_id: str,
    dados: AlunoUpdate,
    db: Session = Depends(get_db)
):
    aluno = db.query(AlunoDB).filter(AlunoDB.id == aluno_id.upper()).first()

    if aluno is None:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")

    if dados.nome is not None:
        aluno.nome = dados.nome

    if dados.email is not None:
        aluno.email = dados.email

    if dados.curso is not None:
        curso = dados.curso.upper()
        if curso not in ["GES", "GEC"]:
            raise HTTPException(status_code=400, detail="Curso deve ser GES ou GEC")
        aluno.curso = curso

    db.commit()
    db.refresh(aluno)

    return aluno_to_dict(aluno)


@app.delete("/api/v1/alunos/{aluno_id}")
def deletar_aluno(aluno_id: str, db: Session = Depends(get_db)):
    aluno = db.query(AlunoDB).filter(AlunoDB.id == aluno_id.upper()).first()

    if aluno is None:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")

    aluno_removido = aluno_to_dict(aluno)

    db.delete(aluno)
    db.commit()

    return {"removido": aluno_removido}


@app.delete("/api/v1/alunos/")
def resetar_alunos(db: Session = Depends(get_db)):
    db.query(AlunoDB).delete()
    db.commit()

    return {"mensagem": "Lista de alunos resetada"}