import pytest


@pytest.fixture(autouse=True)
def isolated_delivery_config(monkeypatch):
    # Impede que a configuração local ative envios em testes de outras etapas.
    monkeypatch.setenv("EMAIL_MODE", "DISABLED")
    monkeypatch.setenv("TEAMS_MODE", "DISABLED")
    for name, value in {
        "APP_PUBLIC_URL": "http://127.0.0.1:8001",
        "SMTP_TIMEOUT": "5",
        "TEAMS_TIMEOUT": "5",
        "NOTIFY_MAX_ATTEMPTS": "3",
        "NOTIFY_RETRY_SECONDS": "10",
        "NOTIFY_POLL_SECONDS": "1",
        "NOTIFY_LEASE_SECONDS": "60",
    }.items():
        monkeypatch.setenv(name, value)
    for name in (
        "SMTP_HOST",
        "SMTP_USERNAME",
        "SMTP_PASSWORD",
        "TEAMS_WEBHOOK_URL",
        "TEAMS_MOCK_URL",
    ):
        monkeypatch.setenv(name, "")
