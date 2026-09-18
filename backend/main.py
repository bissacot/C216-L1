from fastapi import FastAPI, HTTPException

app = FastAPI(title="C216 L1 API")


@app.get("/")
def home():
    return {"message": "API C216 L1 funcionando!"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/saudacao/{nome}")
def saudacao(nome: str):
    if not nome.strip():
        raise HTTPException(status_code=400, detail="Nome inválido")

    return {"message": f"Olá, {nome}!"}


@app.get("/dobro/{numero}")
def dobro(numero: int):
    return {"resultado": numero * 2}