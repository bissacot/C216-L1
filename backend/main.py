from fastapi import FastAPI

app = FastAPI(title="C216 L1 API")


@app.get("/")
def home():
    return {"message": "API C216 L1 funcionando!"}


@app.get("/health")
def health():
    return {"status": "ok"}