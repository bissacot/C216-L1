import pytest


@pytest.mark.parametrize(
    ("path", "first", "second", "query"),
    [
        (
            "/requesters",
            {
                "name": "  Pessoa  ",
                "email": "  DEMO@Example.ORG ",
                "department": "Laboratório",
            },
            {"name": "Outra", "email": "outra@example.org"},
            "borat",
        ),
        (
            "/categories",
            {"name": "Hardware", "description": "Equipamentos"},
            {"name": "Software"},
            "uipam",
        ),
    ],
)
def test_catalog_crud_search_and_pagination(client, path, first, second, query):
    created = client.post(path, json=first)
    assert created.status_code == 201
    item = created.json()
    if path == "/requesters":
        assert item["email"] == "demo@example.org" and item["name"] == "Pessoa"
    url = f"{path}/{item['id']}"
    assert client.get(url).json() == item
    assert client.post(path, json=first).status_code == 409
    other = client.post(path, json=second).json()
    assert client.put(url, json=second).status_code == 409
    assert client.get(url).json() == item
    filtered = client.get(path, params={"q": query.upper()}).json()
    assert filtered["items"] == [item] and filtered["total"] == 1
    pages = [
        client.get(path, params={"page": n, "page_size": 1}).json() for n in (1, 2, 3)
    ]
    assert [p["total"] for p in pages] == [2, 2, 2]
    assert {p["items"][0]["id"] for p in pages[:2]} == {item["id"], other["id"]}
    assert pages[2]["items"] == []
    renamed = {**first, "name": "Renomeado"}
    assert client.put(url, json=renamed).json()["name"] == "Renomeado"
    deleted = client.delete(url)
    assert deleted.status_code == 204 and not deleted.content
    for r in (client.get(url), client.put(url, json=renamed), client.delete(url)):
        assert r.status_code == 404 and r.json()["detail"]


@pytest.mark.parametrize(
    ("path", "data"),
    [
        ("/requesters", {"name": "Pessoa", "email": "inválido"}),
        ("/requesters", {"email": "pessoa@example.org"}),
        ("/categories", {"name": "  "}),
        ("/categories", {"name": "x" * 101}),
        ("/categories", {"name": "Nova", "unknown": "segredo"}),
        ("/tickets", {"title": "Incompleto"}),
    ],
)
def test_invalid_bodies_are_sanitized(client, path, data):
    response = client.post(path, json=data)
    assert response.status_code == 422
    assert all("input" not in e and "ctx" not in e for e in response.json()["detail"])


def test_deletion_of_linked_catalog_entries(client, opened, ticket_input):
    for kind, field in (("requesters", "requester_id"), ("categories", "category_id")):
        url = f"/{kind}/{ticket_input[field]}"
        assert client.delete(url).status_code == 409
        assert client.get(url).status_code == 200
