from app.models import Notification
from app.models.enums import NotificationStatus
from app.repositories.records import find
from app.services.errors import Conflict, NotFound


def retry_failed(db, notification_id):
    row = find(db, Notification, notification_id, lock=True)
    if row is None:
        raise NotFound("Notificação inexistente.")
    if row.status != NotificationStatus.FAILED or row.processing:
        raise Conflict("Somente notificações com falha podem ser reagendadas.")
    row.status = NotificationStatus.PENDING
    row.cycle_attempt = 0
    row.next_attempt_at = None
    db.flush()
    return row
