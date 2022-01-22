from typing import Union, List
from django.db.models import QuerySet, Model
from aria.audit_logs.models import LogEntry
from django.contrib.contenttypes.models import ContentType


def logs_for_instance_list(*, instance: Model) -> Union[QuerySet, LogEntry]:
    """
    Generic get service meant to be reused in local get services
    For example:

    def logs_for_instance_list(*, user: User) -> Union[Queryset, NoteEntry]:
        return logs_for_instance_list(instance=user)

    Return value: List of logs belloning to instance, if any.
    """

    content_type = ContentType.objects.get_for_model(instance)

    return LogEntry.objects.filter(content_type=content_type, object_id=instance.id)
