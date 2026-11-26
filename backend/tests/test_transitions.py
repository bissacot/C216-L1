from itertools import product

import pytest

from app.models import Ticket
from app.models.enums import TicketStatus
from app.schemas.tickets import StatusChange
from app.services.errors import Conflict, InvalidInput
from app.services.tickets import transition_changes

ALLOWED = {
    ("OPEN", "IN_PROGRESS"),
    ("OPEN", "CANCELLED"),
    ("IN_PROGRESS", "RESOLVED"),
    ("IN_PROGRESS", "CANCELLED"),
}


@pytest.mark.parametrize(("source", "target"), list(product(TicketStatus, repeat=2)))
def test_transition_matrix(source, target):
    ticket = Ticket(status=source, assignee="Plantão")
    request = StatusChange(
        status=target,
        resolution="Corrigido" if target == TicketStatus.RESOLVED else None,
    )
    if (source.value, target.value) in ALLOWED:
        result = transition_changes(ticket, request)
        assert result["status"] == target
        if target == TicketStatus.RESOLVED:
            assert result["resolution"] == "Corrigido"
            assert result["resolved_at"].utcoffset().total_seconds() == 0
    else:
        with pytest.raises(Conflict):
            transition_changes(ticket, request)


@pytest.mark.parametrize(
    ("current", "data"),
    [
        ("OPEN", {"status": "IN_PROGRESS"}),
        ("IN_PROGRESS", {"status": "RESOLVED"}),
        ("OPEN", {"status": "CANCELLED", "resolution": "não se aplica"}),
        ("OPEN", {"status": "CANCELLED", "assignee": "plantão"}),
    ],
)
def test_transition_requires_appropriate_fields(current, data):
    with pytest.raises(InvalidInput):
        transition_changes(Ticket(status=TicketStatus(current)), StatusChange(**data))
