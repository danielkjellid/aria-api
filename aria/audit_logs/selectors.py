from django.contrib.contenttypes.models import ContentType
from django.db.models import Model

from aria.audit_logs.models import LogEntry
from aria.audit_logs.schemas.records import LogEntryChangeRecord, LogEntryRecord


def log_entry_list_for_instance(model: Model, *, obj_id: int) -> list[LogEntryRecord]:
    """
    Generic get service meant to be reused in local get services
    For example:

    def some_service(*, user: User) -> None:
        ...
        logs = log_entry_list_for_instance(User, id=user.id)
        ...
        return

    Return value: List of LogEntryRecords belonging to instance, if any.
    """

    content_type = ContentType.objects.get_for_model(model)
    audit_logs = (
        LogEntry.objects.filter(content_type=content_type, object_id=obj_id)
        .prefetch_related("author", "content_object")
        .order_by("-created_at")
    )

    return [
        LogEntryRecord(
            id=log.id,
            author_id=log.author_id if log.author_id else None,
            change=LogEntryChangeRecord(
                field=log.change["field"],
                old_value=log.change["old_value"],
                new_value=log.change["new_value"],
            ),
            created_at=log.created_at,
        )
        for log in audit_logs
    ]
