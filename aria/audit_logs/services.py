from typing import Dict, Any, Union, List
from django.db.models import Model, ManyToOneRel
from aria.users.models import User
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext as _
from django.utils import timezone


from aria.audit_logs.models import LogEntry


def log_entry_create(
    *,
    author: User,
    instance: Model,
    change_messages: List[Dict[str, Any]],
) -> Union[List[LogEntry], None]:
    """
    Generic method for creating a new logging instance which can be used in other
    update/create services.

    change_messages is a list of messages that should be in the format of:
    [
        {"field": ..., "old_value": ..., "new_value": ...}
        {"field": ..., "old_value": ..., "new_value": ...}
    ]

    The update_model core service will format and changes accordingly.
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
                "Error when creating logging instance, old and new values are equal."
            )
        # Filter out reverse relations to prevent type error, and continue
        # to the next iteration.
        if isinstance(instance._meta.get_field(field), ManyToOneRel):
            continue

        content_type = ContentType.objects.get_for_model(instance)
        new_log_entry = LogEntry(
            author=author,
            content_type=content_type,
            content_object=instance,
            object_id=instance.id,
            change=change_message,
            date_of_change=timezone.now(),
        )

        entries_to_create.append(new_log_entry)

    created_entries = LogEntry.objects.bulk_create(entries_to_create)

    return created_entries
