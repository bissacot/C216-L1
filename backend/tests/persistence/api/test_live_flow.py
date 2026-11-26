"""Fluxo HTTP em dois processos Uvicorn, ambos no PostgreSQL descartável da suíte."""

from live_server import isolated_database, running_api


def test_real_http_flow_survives_api_restart(pg_engine, tmp_path):
    url = isolated_database(pg_engine)

    with running_api(url, tmp_path / "first.log") as api:
        person = api.post(
            "/requesters", json={"name": "Pessoa Demo", "email": "pessoa@example.org"}
        )
        category = api.post("/categories", json={"name": "Hardware"})
        assert person.status_code == category.status_code == 201
        created = api.post(
            "/tickets",
            json={
                "title": "Monitor apagado",
                "description": "Verificar cabo",
                "category_id": category.json()["id"],
                "requester_id": person.json()["id"],
                "priority": "CRITICAL",
            },
        )
        assert created.status_code == 201
        path = f"/tickets/{created.json()['id']}"
        notices = api.get(path + "/notifications").json()
        assert {(n["channel"], n["recipient"], n["status"]) for n in notices} == {
            ("EMAIL", "ti-email", "PENDING"),
            ("TEAMS", "ti-teams", "PENDING"),
        }
        started = api.patch(
            path + "/status", json={"status": "IN_PROGRESS", "assignee": "Plantão"}
        )
        assert started.status_code == 200 and started.json()["assignee"] == "Plantão"
        resolved = api.patch(
            path + "/status", json={"status": "RESOLVED", "resolution": "Cabo trocado"}
        )
        assert resolved.status_code == 200 and resolved.json()["resolved_at"]
        history = api.get(path + "/history").json()
        assert [e["new_value"] for e in history if e["field_name"] == "status"] == [
            "OPEN",
            "IN_PROGRESS",
            "RESOLVED",
        ]
        dashboard = api.get("/dashboard").json()
        assert dashboard["total"] == dashboard["by_status"]["RESOLVED"] == 1
        assert dashboard["notifications"]["PENDING"] == 2

    with running_api(url, tmp_path / "second.log") as api:
        assert api.get(path).json() == resolved.json()
        assert api.get(path + "/history").json() == history
        assert api.get(path + "/notifications").json() == notices
        assert api.get("/dashboard").json() == dashboard


def test_readiness_and_cors_preflight(pg_engine, tmp_path):
    origin = "http://localhost:15180"
    with running_api(
        isolated_database(pg_engine), tmp_path / "cors.log", CORS_ORIGINS=origin
    ) as api:
        assert api.get("/ready").json() == {"status": "ok"}
        headers = {
            "Origin": origin,
            "Access-Control-Request-Method": "PATCH",
            "Access-Control-Request-Headers": "Content-Type, X-Changed-By",
        }
        preflight = api.options("/tickets/1/status", headers=headers)
        assert preflight.status_code == 200
        assert preflight.headers["access-control-allow-origin"] == origin
        headers["Origin"] = "http://localhost:15181"
        denied = api.options("/tickets/1/status", headers=headers)
        assert denied.status_code == 400
        assert "access-control-allow-origin" not in denied.headers
