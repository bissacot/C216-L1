class DomainError(Exception):
    """Falha de negócio com mensagem pública."""


class NotFound(DomainError):
    pass


class Conflict(DomainError):
    pass


class InvalidInput(DomainError):
    pass


class ConfigurationError(DomainError):
    pass
