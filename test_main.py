from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_home():
    response = client.get("/")
    assert response.status_code == 200

def test_criar_aluno():
    response = client.post(
        "/api/v1/alunos/",
        json={
            "nome": "Teste",
            "email": "teste@email.com",
            "curso": "GES"
        }
    )

    assert response.status_code == 200

def test_listar_alunos():
    response = client.get("/api/v1/alunos/")
    assert response.status_code == 200