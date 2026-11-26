from typing import Annotated, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

Identifier = Annotated[int, Field(ge=-(2**31), le=2**31 - 1)]
Name = Annotated[str, StringConstraints(min_length=1, max_length=150)]
TextValue = Annotated[str, StringConstraints(min_length=1)]


class Input(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class Output(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class Pagination(Input):
    page: int = Field(1, ge=1, le=2**31 - 1)
    page_size: int = Field(20, ge=1, le=100)


class PageQuery(Pagination):
    q: str | None = Field(None, min_length=1, max_length=200)


Item = TypeVar("Item")


class Page(BaseModel, Generic[Item]):
    items: list[Item]
    total: int
    page: int
    page_size: int
