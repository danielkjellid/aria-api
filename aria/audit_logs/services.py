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

    created_entries = []

    if not author:
        raise ValueError(
            "Error when creating new logging instance, author cannot be none."
        )

    for change_message in change_messages:
        # Validate that required keys are present in the change_message dict.
        assert change_message["field"], "Required key is missing from change_message."
        assert change_message[
            "old_value"
        ], "Required key is missing from change_message."
        assert change_message[
            "new_value"
        ], "Required key is missing from change_message."

        field = change_message.get("field")
        old_value = change_message.get("old_value")
        new_value = change_message.get("new_value")

        # Validate that there has actually been a loggable change.
        if new_value == old_value:
            raise ValueError(
                "Error when creating logging instance, old and new values are equal."
            )
        # Filter out reverse relations to prevent type error, and early
        # return.
        if isinstance(instance._meta.get_field(field), ManyToOneRel):
            continue

        content_type = ContentType.objects.get_for_model(instance)
        new_log_entry = LogEntry.objects.create(
            user=author,
            content_type=content_type,
            content_object=instance,
            object_id=instance.id,
            change=change_message,
            date_of_change=timezone.now(),
        )

        created_entries.append(new_log_entry)

    return created_entries
