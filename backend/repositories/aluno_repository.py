from sqlalchemy.orm import Session

from backend.models.aluno import Aluno


def criar_aluno(db: Session, nome: str, email: str, curso: str) -> Aluno:
    aluno = Aluno(nome=nome, email=email, curso=curso)
    db.add(aluno)
    db.commit()
    db.refresh(aluno)
    return aluno


def buscar_aluno(db: Session, aluno_id: int) -> Aluno | None:
    return db.get(Aluno, aluno_id)


def listar_alunos(db: Session) -> list[Aluno]:
    return db.query(Aluno).order_by(Aluno.id).all()


def atualizar_aluno(db: Session, aluno: Aluno, dados: dict) -> Aluno:
    for campo, valor in dados.items():
        setattr(aluno, campo, valor)

    db.commit()
    db.refresh(aluno)
    return aluno


def remover_aluno(db: Session, aluno: Aluno) -> None:
    db.delete(aluno)
    db.commit()
