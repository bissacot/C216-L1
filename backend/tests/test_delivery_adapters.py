import http.client
import smtplib
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.enums import Channel
from app.services.delivery.adapters import SMTP, TeamsWebhook, adapter_for
from app.services.delivery.messages import TicketMessage
from app.services.delivery.settings import DeliveryError, Mode
from app.services.delivery.worker import send


@pytest.fixture
def message():
    return TicketMessage(
        17,
        "Falha <monitor>",
        'Descrição <b> & "teste"',
        "Alfa",
        "Lab",
        "Hardware",
        "CRITICAL",
        "OPEN",
        "2026-01-01T10:00:00+00:00",
    )


@pytest.fixture
def smtp(monkeypatch):
    for name, value in {
        "SMTP_FROM": "origem@example.invalid",
        "SMTP_TO": "destino@example.invalid",
        "SMTP_HOST": "127.0.0.1",
        "SMTP_PORT": "1025",
        "SMTP_USE_TLS": "false",
        "SMTP_USE_SSL": "false",
        "SMTP_TIMEOUT": "2",
    }.items():
        monkeypatch.setenv(name, value)


def test_mail_alternatives_escape_content(message):
    email = message.email(
        "a@example.invalid", "b@example.invalid", "http://localhost:8001"
    )
    plain = email.get_body(preferencelist=("plain",)).get_content()
    html = email.get_body(preferencelist=("html",)).get_content()
    for value in message.fields().values():
        assert value in plain
    assert "<b>" not in html and "&lt;b&gt; &amp; &quot;teste&quot;" in html
    assert "http://localhost:8001/tickets/17" in plain and "/tickets/17" in html
    assert email.is_multipart()


def test_card_envelope_priority_link(message):
    card = message.teams("https://example.org")["attachments"][0]
    assert card["contentType"] == "application/vnd.microsoft.card.adaptive"
    assert card["content"]["actions"][0]["url"] == "https://example.org/tickets/17"
    assert any(
        b.get("weight") == "Bolder" and "CRITICAL" in b["text"]
        for b in card["content"]["body"]
    )
    assert any(
        f["value"] == message.description for f in card["content"]["body"][2]["facts"]
    )


@pytest.mark.parametrize(
    "settings",
    [
        {"SMTP_USE_TLS": "true", "SMTP_USE_SSL": "true"},
        {"SMTP_TIMEOUT": "nan"},
        {"SMTP_PORT": "0"},
        {"SMTP_FROM": "inválido"},
        {"SMTP_USERNAME": "conta"},
        {"SMTP_USE_TLS": "talvez"},
    ],
)
def test_invalid_smtp_config_never_connects(smtp, message, settings, monkeypatch):
    for key, value in settings.items():
        monkeypatch.setenv(key, value)
    factory = Mock()
    monkeypatch.setattr(smtplib, "SMTP", factory)
    with pytest.raises(DeliveryError):
        SMTP().send(message)
    factory.assert_not_called()


@pytest.mark.parametrize(
    ("failure", "expected"),
    [
        (TimeoutError(), "Tempo limite no SMTP."),
        (OSError("segredo"), "Falha na entrega SMTP."),
    ],
)
def test_smtp_errors_sanitized(smtp, message, monkeypatch, failure, expected):
    monkeypatch.setattr(smtplib, "SMTP", Mock(side_effect=failure))
    assert send(SMTP(), message) == expected


def test_live_teams_timeout_is_sanitized(monkeypatch, message):
    monkeypatch.setenv(
        "TEAMS_WEBHOOK_URL", "https://example.invalid/workflow?token=ficticio"
    )
    client = Mock()
    client.getresponse.side_effect = TimeoutError("ficticio")
    monkeypatch.setattr(http.client, "HTTPSConnection", Mock(return_value=client))
    assert send(TeamsWebhook(), message) == "Tempo limite no Teams."
    client.close.assert_called_once()


@pytest.mark.parametrize(
    ("simulated", "url"),
    [
        (False, "http://example.invalid/"),
        (True, "https://example.org/workflow"),
        (False, ""),
    ],
)
def test_invalid_teams_destination(simulated, url, monkeypatch, message):
    monkeypatch.setenv("TEAMS_MOCK_URL" if simulated else "TEAMS_WEBHOOK_URL", url)
    assert (
        send(TeamsWebhook(simulated=simulated), message)
        == "Configuração do destino Teams inválida."
    )


def test_invalid_retry_policy_keeps_api_available(monkeypatch):
    monkeypatch.setenv("NOTIFY_MAX_ATTEMPTS", "0")
    with TestClient(app) as client:
        assert client.get("/health").json() == {"status": "ok"}


def test_local_mock_is_offline(message):
    for channel in Channel:
        assert send(adapter_for(channel, Mode.MOCK), message) is None
