from pydantic import BaseModel, ConfigDict


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

    model_config = ConfigDict(from_attributes=True)
