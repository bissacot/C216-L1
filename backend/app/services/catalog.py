from app.models import Category, Requester, Ticket
from app.repositories import records
from app.services.errors import NotFound

LABELS = {Requester: "Solicitante", Category: "Categoria", Ticket: "Chamado"}


def require(session, model, record_id, *, lock=False):
    record = records.find(session, model, record_id, lock=lock)
    if record is None:
        raise NotFound(f"{LABELS[model]} inexistente.")
    return record


def create(session, model, data):
    return records.save(session, model(**data.model_dump()))


def replace(session, model, record_id, data):
    record = require(session, model, record_id, lock=True)
    for field, value in data.model_dump().items():
        setattr(record, field, value)
    return records.save(session, record)


def delete(session, model, record_id):
    records.remove(session, require(session, model, record_id, lock=True))
