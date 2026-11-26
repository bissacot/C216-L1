import math
import os
from dataclasses import dataclass
from enum import Enum
from urllib.parse import urlsplit

from app.models.enums import Channel


class Mode(str, Enum):
    DISABLED = "DISABLED"
    MOCK = "MOCK"
    LIVE = "LIVE"


class DeliveryError(Exception):
    """Mensagem pública fixa e segura para a outbox."""


def flag(name: str) -> bool:
    value = os.getenv(name, "false").lower()
    if value not in {"true", "false"}:
        raise DeliveryError("Configuração booleana inválida.")
    return value == "true"


def number(name, default, kind=float, maximum=86400):
    try:
        value = kind(os.getenv(name, str(default)))
        if not math.isfinite(value) or not 0 < value <= maximum:
            raise ValueError
        return value
    except ValueError:
        raise DeliveryError(f"Configuração inválida para {name}.") from None


def public_url():
    base = os.getenv("APP_PUBLIC_URL", "http://127.0.0.1:5180").rstrip("/")
    parts = urlsplit(base)
    if (
        parts.scheme not in {"http", "https"}
        or not parts.hostname
        or parts.username is not None
        or parts.query
        or parts.fragment
    ):
        raise DeliveryError("Endereço público da aplicação inválido.")
    return base


@dataclass(frozen=True)
class Policy:
    max_attempts: int
    backoff: float
    poll: float
    lease: float

    @classmethod
    def load(cls):
        return cls(
            number("NOTIFY_MAX_ATTEMPTS", 3, int, 100),
            number("NOTIFY_RETRY_SECONDS", 10),
            number("NOTIFY_POLL_SECONDS", 1),
            number("NOTIFY_LEASE_SECONDS", 60),
        )


def channel_mode(channel: Channel) -> Mode:
    try:
        return Mode(os.getenv(f"{channel.value}_MODE", "DISABLED").upper())
    except ValueError:
        raise DeliveryError(f"Modo inválido para {channel.value}.") from None
