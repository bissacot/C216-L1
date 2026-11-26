from typing import Annotated

from fastapi import APIRouter, Query

from app.database.session import Database, ReadDatabase
from app.models import Category, Requester
from app.repositories.records import catalog_page
from app.schemas.catalog import (
    CategoryInput,
    CategoryRead,
    RequesterInput,
    RequesterRead,
)
from app.schemas.common import Identifier, Page, PageQuery
from app.services import catalog

router = APIRouter()


@router.post(
    "/requesters",
    tags=["Solicitantes"],
    response_model=RequesterRead,
    status_code=201,
    summary="Cadastrar solicitante",
)
def create_requester(data: RequesterInput, db: Database):
    return catalog.create(db, Requester, data)


@router.get(
    "/requesters",
    tags=["Solicitantes"],
    response_model=Page[RequesterRead],
    summary="Pesquisar solicitantes",
)
def list_requesters(db: ReadDatabase, query: Annotated[PageQuery, Query()]):
    return catalog_page(db, Requester, query)


@router.get(
    "/requesters/{id}",
    tags=["Solicitantes"],
    response_model=RequesterRead,
    summary="Consultar solicitante",
)
def get_requester(id: Identifier, db: ReadDatabase):
    return catalog.require(db, Requester, id)


@router.put(
    "/requesters/{id}",
    tags=["Solicitantes"],
    response_model=RequesterRead,
    summary="Atualizar solicitante",
)
def replace_requester(id: Identifier, data: RequesterInput, db: Database):
    return catalog.replace(db, Requester, id, data)


@router.delete(
    "/requesters/{id}",
    tags=["Solicitantes"],
    status_code=204,
    summary="Excluir solicitante sem chamados",
)
def delete_requester(id: Identifier, db: Database):
    catalog.delete(db, Requester, id)


@router.post(
    "/categories",
    tags=["Categorias"],
    response_model=CategoryRead,
    status_code=201,
    summary="Cadastrar categoria",
)
def create_category(data: CategoryInput, db: Database):
    return catalog.create(db, Category, data)


@router.get(
    "/categories",
    tags=["Categorias"],
    response_model=Page[CategoryRead],
    summary="Pesquisar categorias",
)
def list_categories(db: ReadDatabase, query: Annotated[PageQuery, Query()]):
    return catalog_page(db, Category, query)


@router.get(
    "/categories/{id}",
    tags=["Categorias"],
    response_model=CategoryRead,
    summary="Consultar categoria",
)
def get_category(id: Identifier, db: ReadDatabase):
    return catalog.require(db, Category, id)


@router.put(
    "/categories/{id}",
    tags=["Categorias"],
    response_model=CategoryRead,
    summary="Atualizar categoria",
)
def replace_category(id: Identifier, data: CategoryInput, db: Database):
    return catalog.replace(db, Category, id, data)


@router.delete(
    "/categories/{id}",
    tags=["Categorias"],
    status_code=204,
    summary="Excluir categoria sem chamados",
)
def delete_category(id: Identifier, db: Database):
    catalog.delete(db, Category, id)
