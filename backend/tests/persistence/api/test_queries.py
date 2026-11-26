from datetime import datetime, timedelta, timezone

import pytest

from app.models import Notification, Ticket
from app.models.enums import NotificationStatus


def test_combined_filters_search_sorting_pagination(client, session, ticket_input):
    r2 = client.post(
        "/requesters", json={"name": "Outro", "email": "outro@example.org"}
    ).json()["id"]
    c2 = client.post("/categories", json={"name": "Rede"}).json()["id"]
    start = datetime(2026, 1, 2, 12, tzinfo=timezone.utc)
    ids = []
    for i, data in enumerate(
        [
            {"title": "Alpha 100%", "priority": "HIGH", "assignee": "Equipe A"},
            {
                "title": "Bravo",
                "description": "ALPHA",
                "priority": "HIGH",
                "assignee": "Equipe A",
            },
            {"title": "Charlie", "requester_id": r2, "category_id": c2},
        ]
    ):
        ticket = client.post("/tickets", json={**ticket_input, **data}).json()
        ids.append(ticket["id"])
        session.get(Ticket, ticket["id"]).opened_at = start + timedelta(hours=i)
        session.flush()
    assert (
        client.patch(
            f"/tickets/{ids[1]}/status", json={"status": "IN_PROGRESS"}
        ).status_code
        == 200
    )
    for params, expected in [
        ({"status": "IN_PROGRESS"}, [ids[1]]),
        ({"priority": "HIGH"}, ids[:2]),
        ({"category_id": c2}, ids[2:]),
        ({"requester_id": r2}, ids[2:]),
        ({"assignee": "quipe a"}, ids[:2]),
        ({"q": "alpha"}, ids[:2]),
        ({"q": "%"}, ids[:1]),
        ({"opened_from": start.isoformat(), "opened_to": start.isoformat()}, ids[:1]),
        (
            {
                "q": "alpha",
                "status": "OPEN",
                "priority": "HIGH",
                "category_id": ticket_input["category_id"],
                "requester_id": ticket_input["requester_id"],
                "assignee": "equipe",
                "opened_from": start.isoformat(),
            },
            ids[:1],
        ),
    ]:
        result = client.get(
            "/tickets", params={**params, "sort_by": "title", "order": "asc"}
        ).json()
        assert [r["id"] for r in result["items"]] == expected
        assert result["total"] == len(expected)
    result = client.get("/tickets", params={"page_size": 1, "page": 2}).json()
    assert result["total"] == 3 and result["items"][0]["id"] == ids[1]
    assert [r["id"] for r in client.get("/tickets").json()["items"]] == ids[::-1]


@pytest.mark.parametrize(
    "params",
    [
        {"page": 0},
        {"page_size": 101},
        {"priority": "NONE"},
        {"status": "DONE"},
        {"sort_by": "unknown"},
        {"order": "sideways"},
        {"opened_from": "2026-01-01"},
        {"opened_from": "2026-02-01T00:00:00Z", "opened_to": "2026-01-01T00:00:00Z"},
    ],
)
def test_invalid_ticket_queries(client, params):
    assert client.get("/tickets", params=params).status_code == 422


def test_empty_dashboard(client):
    assert client.get("/dashboard").json() == {
        "total": 0,
        "by_status": {"OPEN": 0, "IN_PROGRESS": 0, "RESOLVED": 0, "CANCELLED": 0},
        "by_priority": {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0},
        "active_critical": 0,
        "by_category": [],
        "average_resolution_seconds": None,
        "recent_tickets": [],
        "notifications": {"PENDING": 0, "SENT": 0, "FAILED": 0},
    }


def test_dashboard_aggregates_and_recent_limit(client, session, ticket_input):
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    unused = client.post("/categories", json={"name": "Vazia"}).json()["id"]
    ids = []
    for i, (status, priority) in enumerate(
        [
            ("OPEN", "CRITICAL"),
            ("IN_PROGRESS", "CRITICAL"),
            ("RESOLVED", "CRITICAL"),
            ("CANCELLED", "CRITICAL"),
            ("OPEN", "HIGH"),
            ("RESOLVED", "MEDIUM"),
        ]
    ):
        id_ = client.post(
            "/tickets", json={**ticket_input, "priority": priority}
        ).json()["id"]
        row = session.get(Ticket, id_)
        row.opened_at = start + timedelta(days=i)
        row.status = status
        if status == "RESOLVED":
            row.resolved_at = row.opened_at + timedelta(seconds=20 if i == 2 else 40)
        ids.append(id_)
        session.flush()
    notices = session.query(Notification).order_by(Notification.id).limit(2).all()
    for notice, status in zip(
        notices, [NotificationStatus.SENT, NotificationStatus.FAILED], strict=True
    ):
        notice.status = status
        notice.attempt_count = 1
        notice.last_attempt_at = start
        notice.sent_at = start if status == NotificationStatus.SENT else None
    session.flush()
    data = client.get("/dashboard").json()
    assert data["total"] == 6 and data["active_critical"] == 2
    assert data["by_status"] == {
        "OPEN": 2,
        "IN_PROGRESS": 1,
        "RESOLVED": 2,
        "CANCELLED": 1,
    }
    assert data["by_priority"] == {"LOW": 0, "MEDIUM": 1, "HIGH": 1, "CRITICAL": 4}
    assert data["average_resolution_seconds"] == 30.0
    assert {c["category_id"]: c["count"] for c in data["by_category"]} == {
        ticket_input["category_id"]: 6,
        unused: 0,
    }
    assert [t["id"] for t in data["recent_tickets"]] == ids[::-1][:5]
    assert data["notifications"] == {"PENDING": 10, "SENT": 1, "FAILED": 1}
