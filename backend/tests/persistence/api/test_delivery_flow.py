import subprocess
import threading
import time
from http.server import ThreadingHTTPServer

import httpx2
import pytest
from live_server import isolated_database, running_api

from app.services.delivery.simulator import MockWorkflow


@pytest.fixture
def mailpit():
    container = subprocess.check_output(
        [
            "docker",
            "run",
            "--detach",
            "--rm",
            "--publish",
            "127.0.0.1::1025",
            "--publish",
            "127.0.0.1::8025",
            "axllent/mailpit:v1.27.4",
        ],
        text=True,
    ).strip()
    try:

        def port(internal):
            address = subprocess.check_output(
                ["docker", "port", container, internal], text=True
            )
            return address.strip().rsplit(":", 1)[1]

        with httpx2.Client(
            base_url="http://127.0.0.1:" + port("8025/tcp"), trust_env=False, timeout=3
        ) as inbox:
            for _ in range(100):
                try:
                    if inbox.get("/readyz").status_code == 200:
                        break
                except httpx2.TransportError:
                    pass
                time.sleep(0.1)
            assert inbox.get("/").status_code == 200
            yield port("1025/tcp"), inbox
    finally:
        subprocess.run(
            ["docker", "stop", container], check=True, stdout=subprocess.DEVNULL
        )


@pytest.fixture
def workflow():
    class Workflow(MockWorkflow):
        def do_POST(self):
            if self.server.failing.is_set():
                # Consumir o POST antes de fechar a conexão preserva o 503 no Windows.
                self.rfile.read(int(self.headers["Content-Length"]))
                return self.send_error(503)
            super().do_POST()

    with ThreadingHTTPServer(("127.0.0.1", 0), Workflow) as server:
        server.failing = threading.Event()
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            yield server
        finally:
            server.shutdown()
            thread.join()


def wait_deliveries(api, ticket, email="SENT", teams="SENT"):
    for _ in range(160):
        response = api.get(f"/tickets/{ticket}/notifications")
        assert response.status_code == 200
        items = {n["channel"]: n for n in response.json()}
        if items["EMAIL"]["status"] == email and items["TEAMS"]["status"] == teams:
            return items
        time.sleep(0.1)
    pytest.fail(f"Estados de entrega inesperados: {items}")


def test_local_mailpit_and_workflow_recovery(pg_engine, tmp_path, mailpit, workflow):
    url = isolated_database(pg_engine)
    smtp_port, inbox = mailpit
    env = {
        "EMAIL_MODE": "LIVE",
        "SMTP_HOST": "127.0.0.1",
        "SMTP_PORT": smtp_port,
        "SMTP_FROM": "origem@example.invalid",
        "SMTP_TO": "equipe@example.invalid",
        "SMTP_USERNAME": "",
        "SMTP_PASSWORD": "",
        "SMTP_USE_TLS": "false",
        "SMTP_USE_SSL": "false",
        "TEAMS_MODE": "MOCK",
        "TEAMS_MOCK_URL": f"http://127.0.0.1:{workflow.server_port}/workflow",
        "APP_PUBLIC_URL": "http://localhost:8001",
        "NOTIFY_POLL_SECONDS": "0.1",
        "NOTIFY_MAX_ATTEMPTS": "1",
    }
    with running_api(url, tmp_path / "off.log") as api:
        requester = api.post(
            "/requesters",
            json={
                "name": "Pessoa Demo",
                "email": "demo@example.org",
                "department": "Lab",
            },
        )
        category = api.post("/categories", json={"name": "Hardware"})
        data = {
            "title": "Monitor <Lab>",
            "description": "Verificar o cabo & fonte.",
            "priority": "HIGH",
            "requester_id": requester.json()["id"],
            "category_id": category.json()["id"],
        }
        first = api.post("/tickets", json=data).json()["id"]
        pending = wait_deliveries(api, first, "PENDING", "PENDING")
        assert all(n["attempt_count"] == 0 for n in pending.values())

    with running_api(url, tmp_path / "enabled.log", **env) as api:
        sent = wait_deliveries(api, first)
        assert (
            sent["EMAIL"]["delivery_mode"] == "LIVE"
            and sent["TEAMS"]["delivery_mode"] == "MOCK"
        )
        assert all(n["sent_at"] and n["attempt_count"] == 1 for n in sent.values())
        (entry,) = inbox.get("/api/v1/messages").json()["messages"]
        mail = inbox.get("/api/v1/message/" + entry["ID"]).json()
        assert (
            f"#{first}" in mail["Subject"]
            and mail["To"][0]["Address"] == "equipe@example.invalid"
        )
        assert "Monitor <Lab>" in mail["Text"] and "Monitor &lt;Lab&gt;" in mail["HTML"]
        assert f"/tickets/{first}" in mail["HTML"]
        card = workflow.last_card["attachments"][0]["content"]
        assert card["actions"][0]["url"].endswith(f"/tickets/{first}")
        assert "HIGH" in card["body"][1]["text"]
        workflow.failing.set()
        second = api.post("/tickets", json=data).json()["id"]
        mixed = wait_deliveries(api, second, teams="FAILED")
        delivery = mixed["TEAMS"]
        assert (
            delivery["next_attempt_at"] is None
            and delivery["last_error"] == "Destino Teams retornou HTTP 503."
        )
        assert api.get(f"/tickets/{second}").json()["status"] == "OPEN"
        workflow.failing.clear()
        retry = api.post(f"/notifications/{delivery['id']}/retry")
        assert retry.status_code == 202
        final = wait_deliveries(api, second)
        assert (
            final["TEAMS"]["attempt_count"] == 2
            and final["TEAMS"]["last_error"] is None
        )
        assert final["EMAIL"]["attempt_count"] == 1
        assert len(inbox.get("/api/v1/messages").json()["messages"]) == 2

    env.update(NOTIFY_MAX_ATTEMPTS="3", NOTIFY_RETRY_SECONDS="2")
    with running_api(url, tmp_path / "restarted.log", **env) as api:
        assert wait_deliveries(api, second) == final
        assert api.post(f"/notifications/{delivery['id']}/retry").status_code == 409
        workflow.failing.set()
        third = api.post("/tickets", json=data).json()["id"]
        waiting = wait_deliveries(api, third, teams="FAILED")
        assert waiting["TEAMS"]["next_attempt_at"]
        workflow.failing.clear()
        recovered = wait_deliveries(api, third)
        assert recovered["TEAMS"]["attempt_count"] == 2
        assert recovered["EMAIL"]["attempt_count"] == 1
