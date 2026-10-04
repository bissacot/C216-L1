import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.routers import alunos as alunos_router


@pytest.fixture
def client():
    alunos_router.alunos.clear()
    alunos_router.proximo_id = 1
    return TestClient(app)


def test_criar_aluno(client):
    response = client.post(
        "/alunos/",
        json={
            "nome": "Gabriel",
            "email": "gabriel@email.com",
            "curso": "Engenharia da Computação",
        },
    )

    assert response.status_code == 201
    assert response.json()["id"] == 1


def test_buscar_aluno(client):
    client.post(
        "/alunos/",
        json={
            "nome": "Gabriel",
            "email": "gabriel@email.com",
            "curso": "Engenharia da Computação",
        },
    )

    response = client.get("/alunos/1")

    assert response.status_code == 200
    assert response.json()["nome"] == "Gabriel"


def test_substituir_aluno(client):
    client.post(
        "/alunos/",
        json={
            "nome": "Gabriel",
            "email": "gabriel@email.com",
            "curso": "Engenharia da Computação",
        },
    )

    response = client.put(
        "/alunos/1",
        json={
            "nome": "Gabriel Bissacot",
            "email": "gabriel@email.com",
            "curso": "Engenharia de Computação",
        },
    )

    assert response.status_code == 200
    assert response.json()["nome"] == "Gabriel Bissacot"


def test_atualizar_aluno(client):
    client.post(
        "/alunos/",
        json={
            "nome": "Gabriel",
            "email": "gabriel@email.com",
            "curso": "Engenharia da Computação",
        },
    )

    response = client.patch(
        "/alunos/1",
        json={"curso": "Engenharia de Computação"},
    )

    assert response.status_code == 200
    assert response.json()["curso"] == "Engenharia de Computação"


def test_remover_aluno(client):
    client.post(
        "/alunos/",
        json={
            "nome": "Gabriel",
            "email": "gabriel@email.com",
            "curso": "Engenharia da Computação",
        },
    )

    response = client.delete("/alunos/1")

    assert response.status_code == 204

    response = client.get("/alunos/1")
    assert response.status_code == 404
