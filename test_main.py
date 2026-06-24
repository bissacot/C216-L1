from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_01_home():
    response = client.get("/")
    assert response.status_code == 200


def test_02_resetar_alunos():
    response = client.delete("/api/v1/alunos/")
    assert response.status_code == 200


def test_03_cadastrar_3_alunos_ges():
    alunos = [
        {"nome": "Gabriel", "email": "gabriel@email.com", "curso": "GES"},
        {"nome": "Joao", "email": "joao@email.com", "curso": "GES"},
        {"nome": "Pedro", "email": "pedro@email.com", "curso": "GES"},
    ]

    for aluno in alunos:
        response = client.post("/api/v1/alunos/", json=aluno)
        assert response.status_code == 200

    response = client.get("/api/v1/alunos/")
    dados = response.json()

    ids = [aluno["id"] for aluno in dados]
    assert "GES1" in ids
    assert "GES2" in ids
    assert "GES3" in ids


def test_04_cadastrar_3_alunos_gec():
    alunos = [
        {"nome": "Maria", "email": "maria@email.com", "curso": "GEC"},
        {"nome": "Ana", "email": "ana@email.com", "curso": "GEC"},
        {"nome": "Carlos", "email": "carlos@email.com", "curso": "GEC"},
    ]

    for aluno in alunos:
        response = client.post("/api/v1/alunos/", json=aluno)
        assert response.status_code == 200

    response = client.get("/api/v1/alunos/")
    dados = response.json()

    ids = [aluno["id"] for aluno in dados]
    assert "GEC1" in ids
    assert "GEC2" in ids
    assert "GEC3" in ids


def test_05_listar_alunos():
    response = client.get("/api/v1/alunos/")
    assert response.status_code == 200
    assert len(response.json()) >= 6


def test_06_buscar_aluno_por_id():
    response = client.get("/api/v1/alunos/GES1")
    assert response.status_code == 200
    assert response.json()["id"] == "GES1"


def test_07_atualizar_aluno():
    response = client.patch(
        "/api/v1/alunos/GES1",
        json={"nome": "Gabriel Atualizado"},
    )

    assert response.status_code == 200
    assert response.json()["nome"] == "Gabriel Atualizado"


def test_08_remover_aluno():
    response = client.delete("/api/v1/alunos/GES3")
    assert response.status_code == 200

    response = client.get("/api/v1/alunos/GES3")
    assert response.status_code == 404