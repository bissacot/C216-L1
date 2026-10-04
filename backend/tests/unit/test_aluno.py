from backend.schemas.aluno import Aluno, AlunoCreate, AlunoUpdate


def test_aluno_create():
    aluno = AlunoCreate(
        nome="Gabriel",
        email="gabriel@email.com",
        curso="Engenharia da Computação",
    )

    assert aluno.nome == "Gabriel"
    assert aluno.email == "gabriel@email.com"
    assert aluno.curso == "Engenharia da Computação"


def test_aluno_com_id():
    aluno = Aluno(
        id=1,
        nome="Gabriel",
        email="gabriel@email.com",
        curso="Engenharia da Computação",
    )

    assert aluno.id == 1
    assert aluno.nome == "Gabriel"


def test_aluno_update_parcial():
    aluno = AlunoUpdate(curso="Engenharia de Computação")

    assert aluno.curso == "Engenharia de Computação"
    assert aluno.nome is None
    assert aluno.email is None
