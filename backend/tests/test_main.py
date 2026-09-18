import pytest
from fastapi.testclient import TestClient

from backend.main import app

@pytest.fixture
def client():
    return TestClient(app)


def test_home(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "API C216 L1 funcionando!"}


def test_health(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_saudacao(client):
    response = client.get("/saudacao/Gabriel")

    assert response.status_code == 200
    assert response.json() == {"message": "Olá, Gabriel!"}


@pytest.mark.parametrize(
    "numero,resultado",
    [
        (2, 4),
        (5, 10),
        (10, 20),
    ],
)
def test_dobro(client, numero, resultado):
    response = client.get(f"/dobro/{numero}")

    assert response.status_code == 200
    assert response.json() == {"resultado": resultado}


def test_dobro_valor_invalido(client):
    response = client.get("/dobro/abc")

    assert response.status_code == 422