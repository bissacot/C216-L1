from pydantic import BaseModel


class AlunoCreate(BaseModel):
    nome: str
    email: str
    curso: str


class AlunoUpdate(BaseModel):
    nome: str | None = None
    email: str | None = None
    curso: str | None = None


class Aluno(AlunoCreate):
    id: int
