from datetime import datetime
from typing import Annotated

from pydantic import EmailStr, Field, field_validator

from app.schemas.common import Input, Name, Output, TextValue

# Endereços fictícios da carga da Etapa 2 também podem ser editados pela API.
DemoEmail = Annotated[
    str,
    Field(pattern=r"^[a-z0-9_+-]+(?:\.[a-z0-9_+-]+)*@example\.invalid$", max_length=80),
]


class RequesterInput(Input):
    name: Name = Field(examples=["Pessoa de teste"])
    email: EmailStr | DemoEmail = Field(max_length=254, examples=["pessoa@example.org"])
    department: Name | None = Field(None, examples=["Suporte"])

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value):
        return value.strip().lower() if isinstance(value, str) else value


class RequesterRead(Output):
    id: int = Field(examples=[1])
    name: str = Field(examples=["Pessoa de teste"])
    email: str = Field(examples=["pessoa@example.org"])
    department: str | None
    created_at: datetime
    updated_at: datetime


class CategoryInput(Input):
    name: Annotated[str, Field(min_length=1, max_length=100, examples=["Hardware"])]
    description: TextValue | None = Field(None, examples=["Equipamentos da equipe"])


class CategoryRead(Output):
    id: int = Field(examples=[1])
    name: str = Field(examples=["Hardware"])
    description: str | None
    created_at: datetime
    updated_at: datetime
