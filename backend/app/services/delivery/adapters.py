import http.client
import json
import os
import smtplib
import ssl
from email.headerregistry import Address
from typing import Protocol
from urllib.parse import urlsplit

from app.models.enums import Channel
from app.services.delivery.messages import TicketMessage
from app.services.delivery.settings import DeliveryError, Mode, flag, number, public_url


class Adapter(Protocol):
    def send(self, message: TicketMessage) -> None: ...


class Simulation:
    def send(self, message: TicketMessage) -> None:
        pass


class SMTP:
    def send(self, message: TicketMessage) -> None:
        host = os.getenv("SMTP_HOST")
        tls, implicit_ssl = flag("SMTP_USE_TLS"), flag("SMTP_USE_SSL")
        username, password = os.getenv("SMTP_USERNAME"), os.getenv("SMTP_PASSWORD")
        if not host or (tls and implicit_ssl) or bool(username) != bool(password):
            raise DeliveryError("Configuração SMTP incompatível ou incompleta.")
        try:
            sender = Address(addr_spec=os.environ["SMTP_FROM"])
            recipient = Address(addr_spec=os.environ["SMTP_TO"])
            if not all(a.username and a.domain for a in (sender, recipient)):
                raise ValueError
        except (KeyError, ValueError, IndexError):
            raise DeliveryError("Endereço SMTP inválido.") from None
        port = number("SMTP_PORT", 465 if implicit_ssl else 25, int, 65535)
        timeout = number("SMTP_TIMEOUT", 10)
        mail = message.email(sender, recipient, public_url())
        context = ssl.create_default_context()
        try:
            client = (
                smtplib.SMTP_SSL(host, port, timeout=timeout, context=context)
                if implicit_ssl
                else smtplib.SMTP(host, port, timeout=timeout)
            )
            with client:
                if tls:
                    client.starttls(context=context)
                if username:
                    client.login(username, password)
                client.send_message(mail)
        except TimeoutError:
            raise DeliveryError("Tempo limite no SMTP.") from None
        except (smtplib.SMTPException, OSError):
            raise DeliveryError("Falha na entrega SMTP.") from None


class TeamsWebhook:
    def __init__(self, *, simulated=False):
        self.simulated = simulated

    def send(self, message: TicketMessage) -> None:
        key = "TEAMS_MOCK_URL" if self.simulated else "TEAMS_WEBHOOK_URL"
        try:
            parts = urlsplit(os.getenv(key, ""))
            host, port = parts.hostname, parts.port
            allowed = (
                parts.scheme == "http"
                and host in {"127.0.0.1", "::1", "localhost", "teams-mock"}
                if self.simulated
                else parts.scheme == "https"
            )
            if not allowed or not host or parts.username is not None or parts.fragment:
                raise ValueError
        except ValueError:
            raise DeliveryError("Configuração do destino Teams inválida.") from None
        timeout = number("TEAMS_TIMEOUT", 10)
        body = json.dumps(message.teams(public_url()), ensure_ascii=False).encode()
        connection = (
            http.client.HTTPConnection
            if self.simulated
            else http.client.HTTPSConnection
        )(host, port, timeout=timeout)
        try:
            path = parts.path or "/"
            if parts.query:
                path += "?" + parts.query
            connection.request(
                "POST", path, body, {"Content-Type": "application/json; charset=utf-8"}
            )
            status = connection.getresponse().status
            if not 200 <= status < 300:
                raise DeliveryError(f"Destino Teams retornou HTTP {status}.")
        except TimeoutError:
            raise DeliveryError("Tempo limite no Teams.") from None
        except (OSError, http.client.HTTPException, ValueError):
            raise DeliveryError("Falha de comunicação com o Teams.") from None
        finally:
            connection.close()


def adapter_for(channel: Channel, mode: Mode) -> Adapter:
    if mode == Mode.MOCK:
        if channel == Channel.TEAMS and os.getenv("TEAMS_MOCK_URL"):
            return TeamsWebhook(simulated=True)
        return Simulation()
    if mode == Mode.LIVE:
        return SMTP() if channel == Channel.EMAIL else TeamsWebhook()
    raise DeliveryError("Canal desativado.")
