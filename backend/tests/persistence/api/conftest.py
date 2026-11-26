import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.database.session import get_read_session, get_session
from app.main import app


@pytest.fixture
def client(session):
    def isolated_session():
        with (
            Session(
                session.get_bind(),
                join_transaction_mode="create_savepoint",
                expire_on_commit=False,
            ) as db,
            db.begin(),
        ):
            yield db

    app.dependency_overrides[get_session] = isolated_session
    app.dependency_overrides[get_read_session] = isolated_session
    try:
        with TestClient(app) as client:
            yield client
    finally:
        del app.dependency_overrides[get_session]
        del app.dependency_overrides[get_read_session]


@pytest.fixture
def ticket_input(client):
    requester = client.post(
        "/requesters", json={"name": "Teste", "email": "teste@example.org"}
    )
    category = client.post("/categories", json={"name": "Suporte"})
    assert requester.status_code == category.status_code == 201
    return {
        "title": "Monitor",
        "description": "Sem imagem",
        "requester_id": requester.json()["id"],
        "category_id": category.json()["id"],
    }


@pytest.fixture
def opened(client, ticket_input):
    response = client.post("/tickets", json=ticket_input)
    assert response.status_code == 201, response.text
    return f"/tickets/{response.json()['id']}"
