from fastapi import APIRouter, HTTPException

from backend.schemas.aluno import Aluno, AlunoCreate, AlunoUpdate

router = APIRouter(prefix="/alunos", tags=["Alunos"])

alunos: dict[int, Aluno] = {}
proximo_id = 1


@router.post("/", response_model=Aluno, status_code=201)
def criar_aluno(dados: AlunoCreate):
    global proximo_id

    aluno = Aluno(id=proximo_id, **dados.model_dump())
    alunos[proximo_id] = aluno
    proximo_id += 1

    return aluno


@router.get("/{aluno_id}", response_model=Aluno)
def buscar_aluno(aluno_id: int):
    aluno = alunos.get(aluno_id)

    if aluno is None:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")

    return aluno


@router.put("/{aluno_id}", response_model=Aluno)
def substituir_aluno(aluno_id: int, dados: AlunoCreate):
    if aluno_id not in alunos:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")

    aluno = Aluno(id=aluno_id, **dados.model_dump())
    alunos[aluno_id] = aluno

    return aluno


@router.patch("/{aluno_id}", response_model=Aluno)
def atualizar_aluno(aluno_id: int, dados: AlunoUpdate):
    aluno = alunos.get(aluno_id)

    if aluno is None:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")

    dados_atualizados = dados.model_dump(exclude_unset=True)
    aluno_atualizado = aluno.model_copy(update=dados_atualizados)
    alunos[aluno_id] = aluno_atualizado

    return aluno_atualizado


@router.delete("/{aluno_id}", status_code=204)
def remover_aluno(aluno_id: int):
    if aluno_id not in alunos:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")

    del alunos[aluno_id]
