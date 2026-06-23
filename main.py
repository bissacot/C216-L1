from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr

app = FastAPI(title="Gerenciador de Alunos")

alunos = {}
matriculas = {"GES": 0, "GEC": 0}


class AlunoCreate(BaseModel):
    nome: str
    email: EmailStr
    curso: str


class AlunoUpdate(BaseModel):
    nome: str | None = None
    email: EmailStr | None = None
    curso: str | None = None


@app.get("/")
def home():
    return {"mensagem": "API funcionando!"}


@app.post("/api/v1/alunos/")
def criar_aluno(aluno: AlunoCreate):
    curso = aluno.curso.upper()

    if curso not in ["GES", "GEC"]:
        raise HTTPException(status_code=400, detail="Curso deve ser GES ou GEC")

    matriculas[curso] += 1
    matricula = matriculas[curso]
    aluno_id = f"{curso}{matricula}"

    novo_aluno = {
        "id": aluno_id,
        "nome": aluno.nome,
        "email": aluno.email,
        "curso": curso,
        "matricula": matricula
    }

    alunos[aluno_id] = novo_aluno
    return novo_aluno


@app.get("/api/v1/alunos/")
def listar_alunos():
    return list(alunos.values())


@app.get("/api/v1/alunos/{aluno_id}")
def buscar_aluno(aluno_id: str):
    if aluno_id not in alunos:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")
    return alunos[aluno_id]


@app.patch("/api/v1/alunos/{aluno_id}")
def atualizar_aluno(aluno_id: str, dados: AlunoUpdate):
    if aluno_id not in alunos:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")

    if dados.nome is not None:
        alunos[aluno_id]["nome"] = dados.nome

    if dados.email is not None:
        alunos[aluno_id]["email"] = dados.email

    if dados.curso is not None:
        curso = dados.curso.upper()
        if curso not in ["GES", "GEC"]:
            raise HTTPException(status_code=400, detail="Curso deve ser GES ou GEC")
        alunos[aluno_id]["curso"] = curso

    return alunos[aluno_id]


@app.delete("/api/v1/alunos/{aluno_id}")
def deletar_aluno(aluno_id: str):
    if aluno_id not in alunos:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")

    aluno_removido = alunos.pop(aluno_id)
    return {"removido": aluno_removido}


@app.delete("/api/v1/alunos/")
def resetar_alunos():
    alunos.clear()
    return {"mensagem": "Lista de alunos resetada"}