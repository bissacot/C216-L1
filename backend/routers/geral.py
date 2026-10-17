from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.get("/")
def home():
    return {"message": "API C216 L1 funcionando!"}


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/saudacao/{nome}")
def saudacao(nome: str):
    if not nome.strip():
        raise HTTPException(status_code=400, detail="Nome inválido")

    return {"message": f"Olá, {nome}!"}


@router.get("/dobro/{numero}")
def dobro(numero: int):
    return {"resultado": numero * 2}
