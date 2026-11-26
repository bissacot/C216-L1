import pytest
from fastapi.testclient import TestClient

from backend.main import app, create_app


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


@pytest.mark.parametrize("method", ["GET", "POST", "PUT", "PATCH", "DELETE"])
def test_preflight_da_interface(monkeypatch, method):
    origin = "http://frontend.test:5173"
    monkeypatch.setenv("CORS_ORIGINS", f"http://outro.test, {origin}")
    with TestClient(create_app()) as client:
        response = client.options(
            "/alunos/",
            headers={
                "Origin": origin,
                "Access-Control-Request-Method": method,
                "Access-Control-Request-Headers": "Content-Type",
            },
        )
        assert response.status_code == 200
        assert response.headers["access-control-allow-origin"] == origin
        actual = client.get("/health", headers={"Origin": origin})
        assert actual.headers["access-control-allow-origin"] == origin


def test_preflight_rejeita_origem_desconhecida(monkeypatch):
    monkeypatch.setenv("CORS_ORIGINS", "http://frontend.test:5173")
    with TestClient(create_app()) as client:
        response = client.options(
            "/alunos/",
            headers={
                "Origin": "http://outra.test",
                "Access-Control-Request-Method": "POST",
            },
        )
    assert response.status_code == 400
    assert "access-control-allow-origin" not in response.headers


def test_configuracao_rejeita_origem_universal(monkeypatch):
    monkeypatch.setenv("CORS_ORIGINS", "*")
    with pytest.raises(ValueError, match="origens explícitas"):
        create_app()
