from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from backend.database.base import Base


class Aluno(Base):
    __tablename__ = "alunos"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(150), nullable=False)
    curso: Mapped[str] = mapped_column(String(100), nullable=False)
