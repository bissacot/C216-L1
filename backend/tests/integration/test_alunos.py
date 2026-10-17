def test_criar_aluno(client):
    resposta = client.post(
        "/alunos/",
        json={
            "nome": "Gabriel",
            "email": "gabriel@teste.com",
            "curso": "Engenharia da Computação",
        },
    )

    assert resposta.status_code == 201

    aluno = resposta.json()
    assert aluno["id"] == 1
    assert aluno["nome"] == "Gabriel"
    assert aluno["email"] == "gabriel@teste.com"


def test_buscar_aluno(client):
    criacao = client.post(
        "/alunos/",
        json={
            "nome": "Maria",
            "email": "maria@teste.com",
            "curso": "Engenharia de Software",
        },
    )

    aluno_id = criacao.json()["id"]

    resposta = client.get(f"/alunos/{aluno_id}")

    assert resposta.status_code == 200
    assert resposta.json()["nome"] == "Maria"


def test_substituir_aluno(client):
    criacao = client.post(
        "/alunos/",
        json={
            "nome": "Pedro",
            "email": "pedro@teste.com",
            "curso": "Computação",
        },
    )

    aluno_id = criacao.json()["id"]

    resposta = client.put(
        f"/alunos/{aluno_id}",
        json={
            "nome": "Pedro Silva",
            "email": "pedro.silva@teste.com",
            "curso": "Engenharia da Computação",
        },
    )

    assert resposta.status_code == 200
    assert resposta.json()["nome"] == "Pedro Silva"
    assert resposta.json()["curso"] == "Engenharia da Computação"


def test_atualizar_aluno(client):
    criacao = client.post(
        "/alunos/",
        json={
            "nome": "Ana",
            "email": "ana@teste.com",
            "curso": "Computação",
        },
    )

    aluno_id = criacao.json()["id"]

    resposta = client.patch(
        f"/alunos/{aluno_id}",
        json={"curso": "Engenharia da Computação"},
    )

    assert resposta.status_code == 200
    assert resposta.json()["nome"] == "Ana"
    assert resposta.json()["curso"] == "Engenharia da Computação"


def test_remover_aluno(client):
    criacao = client.post(
        "/alunos/",
        json={
            "nome": "Carlos",
            "email": "carlos@teste.com",
            "curso": "Computação",
        },
    )

    aluno_id = criacao.json()["id"]

    resposta = client.delete(f"/alunos/{aluno_id}")

    assert resposta.status_code == 204

    consulta = client.get(f"/alunos/{aluno_id}")

    assert consulta.status_code == 404


def test_listar_alunos(client):
    client.post(
        "/alunos/",
        json={
            "nome": "Gabriel",
            "email": "gabriel@teste.com",
            "curso": "Computação",
        },
    )

    resposta = client.get("/alunos/")

    assert resposta.status_code == 200
    assert len(resposta.json()) == 1
    assert resposta.json()[0]["nome"] == "Gabriel"
