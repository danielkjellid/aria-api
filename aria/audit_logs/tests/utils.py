from django.contrib.contenttypes.models import ContentType
from django.db.models import Model
from django.utils import timezone

from aria.audit_logs.models import LogEntry
from aria.audit_logs.types import ChangeMessage
from aria.users.models import User
from aria.users.tests.utils import create_user


def create_log_entry(
    model: Model,
    *,
    obj_id: int,
    author: User | None = None,
    change_message: ChangeMessage,
) -> LogEntry:
    """
    Test utility for creating a log entry.
    """
    content_type = ContentType.objects.get_for_model(model)

    if author is None:
        author = create_user(email="author@example.com")

    log_entry = LogEntry.objects.create(
        author=author,
        content_type=content_type,
        object_id=obj_id,
        change=change_message,
        created_at=timezone.now(),
    )

    return log_entry
