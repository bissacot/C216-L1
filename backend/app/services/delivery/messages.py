from dataclasses import dataclass
from email.message import EmailMessage
from html import escape


@dataclass(frozen=True)
class TicketMessage:
    id: int
    title: str
    description: str
    requester: str
    department: str | None
    category: str
    priority: str
    status: str
    opened_at: str

    def fields(self):
        return {
            "Chamado": f"#{self.id}",
            "Título": self.title,
            "Descrição": self.description,
            "Solicitante": self.requester,
            "Departamento": self.department or "Não informado",
            "Categoria": self.category,
            "Prioridade": self.priority,
            "Status": self.status,
            "Abertura": self.opened_at,
        }

    def email(self, sender, recipient, public_base):
        url = f"{public_base}/tickets/{self.id}"
        fields = self.fields()
        message = EmailMessage()
        message["Subject"] = f"HelpDesk Hub | Chamado #{self.id}"
        message["From"] = sender
        message["To"] = recipient
        message.set_content(
            "\n".join(f"{label}: {value}" for label, value in fields.items())
            + f"\nAbrir chamado: {url}"
        )
        rows = "".join(
            f"<dt>{label}</dt><dd>{escape(value)}</dd>"
            for label, value in fields.items()
        )
        link = escape(url, quote=True)
        message.add_alternative(
            f'<dl>{rows}</dl><p><a href="{link}">Abrir chamado</a></p>',
            subtype="html",
        )
        return message

    def teams(self, public_base):
        fields = self.fields()
        return {
            "type": "message",
            "attachments": [
                {
                    "contentType": "application/vnd.microsoft.card.adaptive",
                    "content": {
                        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                        "type": "AdaptiveCard",
                        "version": "1.2",
                        "body": [
                            {
                                "type": "TextBlock",
                                "text": f"HelpDesk Hub | Chamado #{self.id}",
                                "weight": "Bolder",
                                "wrap": True,
                            },
                            {
                                "type": "TextBlock",
                                "text": f"Prioridade: {self.priority}",
                                "weight": "Bolder",
                                "color": "Attention",
                            },
                            {
                                "type": "FactSet",
                                "facts": [
                                    {"title": k, "value": v}
                                    for k, v in fields.items()
                                    if k not in {"Chamado", "Prioridade"}
                                ],
                            },
                        ],
                        "actions": [
                            {
                                "type": "Action.OpenUrl",
                                "title": "Abrir chamado",
                                "url": f"{public_base}/tickets/{self.id}",
                            }
                        ],
                    },
                }
            ],
        }
