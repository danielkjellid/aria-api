from typing import List

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import FieldDoesNotExist
from django.db.models import ManyToOneRel, Model
from django.utils import timezone

from aria.audit_logs.models import LogEntry
from aria.audit_logs.schemas.records import LogEntryChangeRecord, LogEntryRecord
from aria.audit_logs.types import ChangeMessage
from aria.users.models import User


def log_entries_create(
    *,
    author: User,
    instance: Model,
    change_messages: List[ChangeMessage],
) -> list[LogEntryRecord]:
    """
    Generic method for creating a new logging instance which can be used in other
    update/create services.

    change_messages is a list of messages that should be in the format of:
    [
        {"field": ..., "old_value": ..., "new_value": ...}
        {"field": ..., "old_value": ..., "new_value": ...}
    ]

    The update_model core service will format and change accordingly.
    """

    entries_to_create = []

    if not author:
        raise ValueError(
            "Error when creating new logging instance, author cannot be none."
        )

    for change_message in change_messages:

        field = change_message.get("field", None)
        old_value = change_message.get("old_value", None)
        new_value = change_message.get("new_value", None)

        if field is None or old_value is None or new_value is None:
            raise ValueError(
                "Error when creating logging instance, one of the required keys are none."
            )

        # Validate that there has actually been a loggable change.
        if new_value == old_value:
            raise ValueError(
                f"Error when creating logging instance, old ({old_value}) and new ({new_value}) values are equal"
            )

        # Check if field actually exist on model, if not, continue to next
        # iterations.
        try:
            instance._meta.get_field(field)

            # Filter out reverse relations to prevent type error, and continue
            # to the next iteration.
            if isinstance(instance._meta.get_field(field), ManyToOneRel):
                continue

            content_type = ContentType.objects.get_for_model(instance)
            new_log_entry = LogEntry(
                author=author,
                content_type=content_type,
                content_object=instance,
                object_id=instance.pk,
                change=change_message,
                created_at=timezone.now(),
            )

            entries_to_create.append(new_log_entry)
        except FieldDoesNotExist:
            continue

    created_entries = LogEntry.objects.bulk_create(entries_to_create)

    return [
        LogEntryRecord(
            id=entry.id,
            author_id=entry.author_id,  # type: ignore
            change=LogEntryChangeRecord(
                field=entry.change["field"],
                old_value=entry.change["old_value"],
                new_value=entry.change["new_value"],
            ),
            created_at=entry.created_at,
        )
        for entry in created_entries
    ]
