import pytest
from sqlalchemy import func, select, text

from app.database.seed import seed_demo
from app.models import Notification, Ticket, TicketHistory


def test_open_history_edit_resolve_and_close(client, ticket_input, monkeypatch):
    monkeypatch.setenv("NOTIFY_EMAIL_RECIPIENT", "ti-email")
    monkeypatch.setenv("NOTIFY_TEAMS_RECIPIENT", "ti-teams")
    actor = {"X-Changed-By": "Plantao A"}
    response = client.post("/tickets", json=ticket_input, headers=actor)
    assert response.status_code == 201
    ticket = response.json()
    url = f"/tickets/{ticket['id']}"
    assert client.get(url).json() == ticket and ticket["status"] == "OPEN"
    notices = client.get(url + "/notifications").json()
    assert {(n["channel"], n["recipient"]) for n in notices} == {
        ("EMAIL", "ti-email"),
        ("TEAMS", "ti-teams"),
    }
    assert all(n["status"] == "PENDING" and n["attempt_count"] == 0 for n in notices)
    assert client.put(url, json=ticket_input).status_code == 200
    (creation,) = client.get(url + "/history").json()
    assert (
        creation["field_name"],
        creation["old_value"],
        creation["new_value"],
        creation["changed_by"],
    ) == ("status", None, "OPEN", "Plantao A")
    updated = {**ticket_input, "priority": "HIGH", "assignee": "Equipe A"}
    assert client.put(url, json=updated).status_code == 200
    assert (
        client.patch(url + "/status", json={"status": "IN_PROGRESS"}).status_code == 200
    )
    assert client.put(url, json=ticket_input).status_code == 422
    assert client.delete(url).status_code == 409
    resolved = client.patch(
        url + "/status", json={"status": "RESOLVED", "resolution": "Cabo substituído."}
    )
    assert resolved.status_code == 200
    assert (
        resolved.json()["resolved_at"]
        and resolved.json()["resolution"] == "Cabo substituído."
    )
    events = client.get(url + "/history").json()
    assert [
        (e["old_value"], e["new_value"]) for e in events if e["field_name"] == "status"
    ] == [(None, "OPEN"), ("OPEN", "IN_PROGRESS"), ("IN_PROGRESS", "RESOLVED")]
    assert {e["field_name"] for e in events} == {
        "status",
        "priority",
        "assignee",
        "resolution",
        "resolved_at",
    }
    assert client.put(url, json=updated).status_code == 409
    assert client.delete(url).status_code == 409
    assert client.get(url + "/notifications").json() == notices


@pytest.mark.parametrize("active", [False, True])
def test_cancel_and_cascade(client, opened, ticket_input, active, session):
    if active:
        assert (
            client.patch(
                opened + "/status", json={"status": "IN_PROGRESS", "assignee": "TI"}
            ).status_code
            == 200
        )
    assert client.delete(opened).status_code == 409
    assert (
        client.patch(opened + "/status", json={"status": "CANCELLED"}).status_code
        == 200
    )
    assert client.put(opened, json=ticket_input).status_code == 409
    assert client.patch(opened + "/status", json={"status": "OPEN"}).status_code == 409
    assert client.delete(opened).status_code == 204
    for path in ("", "/history", "/notifications"):
        assert client.get(opened + path).status_code == 404
    for model in (TicketHistory, Notification):
        assert session.scalar(select(func.count()).select_from(model)) == 0


def test_missing_resources(client, ticket_input):
    for field in ("requester_id", "category_id"):
        assert (
            client.post("/tickets", json={**ticket_input, field: -994}).status_code
            == 404
        )
    for r in (
        client.get("/tickets/-994"),
        client.put("/tickets/-994", json=ticket_input),
        client.patch("/tickets/-994/status", json={"status": "CANCELLED"}),
        client.delete("/tickets/-994"),
    ):
        assert r.status_code == 404


def test_status_bypass_and_invalid_transitions(client, opened, ticket_input):
    for key, value in [
        ("status", "RESOLVED"),
        ("resolved_at", "2026-01-01T00:00:00Z"),
        ("resolution", "Pronto"),
    ]:
        assert client.put(opened, json={**ticket_input, key: value}).status_code == 422
        assert (
            client.post("/tickets", json={**ticket_input, key: value}).status_code
            == 422
        )
    assert (
        client.patch(
            opened + "/status", json={"status": "RESOLVED", "resolution": "x"}
        ).status_code
        == 409
    )
    assert (
        client.patch(opened + "/status", json={"status": "IN_PROGRESS"}).status_code
        == 422
    )
    assert (
        client.patch(
            opened + "/status", json={"status": "IN_PROGRESS", "assignee": "A"}
        ).status_code
        == 200
    )
    assert (
        client.patch(
            opened + "/status", json={"status": "RESOLVED", "resolution": "  "}
        ).status_code
        == 422
    )
    assert client.get(opened).json()["status"] == "IN_PROGRESS"


def test_open_rolls_back_every_record_when_second_delivery_fails(
    client, session, ticket_input
):
    session.execute(text("ALTER TABLE notifications ADD CHECK (channel <> 'TEAMS')"))
    failed = client.post("/tickets", json=ticket_input)
    assert failed.status_code == 409
    assert list(failed.json()) == ["detail"]
    assert "INSERT" not in failed.text and "psycopg" not in failed.text
    for model in (Ticket, TicketHistory, Notification):
        assert session.scalar(select(func.count()).select_from(model)) == 0


def test_failed_history_rolls_back_ticket_update(client, session, opened, ticket_input):
    session.execute(
        text("ALTER TABLE ticket_history ADD CHECK (field_name <> 'title')")
    )
    assert (
        client.put(opened, json={**ticket_input, "title": "Alterado"}).status_code
        == 409
    )
    assert client.get(opened).json()["title"] == ticket_input["title"]
    assert len(client.get(opened + "/history").json()) == 1


def test_seed_remains_silent_and_negative_ids_are_accessible(client, session):
    seed_demo(session)
    session.flush()
    assert client.get("/tickets/-1").status_code == 200
    assert client.get("/tickets/-1/notifications").json() == []
    requester = client.get("/requesters", params={"q": "alfa@example.invalid"}).json()[
        "items"
    ][0]
    edited = client.put(
        f"/requesters/{requester['id']}",
        json={
            "name": "Demo editado",
            "email": requester["email"],
            "department": "Teste",
        },
    )
    assert edited.status_code == 200 and edited.json()["email"] == requester["email"]


def test_commit_failure_rolls_back_before_http_success(client, session, ticket_input):
    from sqlalchemy import event
    from sqlalchemy.exc import OperationalError
    from sqlalchemy.orm import Session

    def fail_commit(db):
        raise OperationalError("SQL interno", {}, RuntimeError("detalhe privado"))

    event.listen(Session, "before_commit", fail_commit)
    try:
        response = client.post("/tickets", json=ticket_input)
    finally:
        event.remove(Session, "before_commit", fail_commit)
    assert response.status_code == 500
    assert response.json() == {"detail": "Falha de persistência."}
    for model in (Ticket, TicketHistory, Notification):
        assert session.scalar(select(func.count()).select_from(model)) == 0
