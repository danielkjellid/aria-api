from typing import Union

from django.contrib.contenttypes.models import ContentType
from django.db.models import Model, QuerySet

from aria.audit_logs.models import LogEntry


def log_list_for_instance(model: Model, *, id: int) -> Union[QuerySet, LogEntry]:
    """
    Generic get service meant to be reused in local get services
    For example:

    def log_list_for_instance(*, user: User) -> Union[Queryset, NoteEntry]:
        return log_list_for_instance(instance=user)

    Return value: List of logs belloning to instance, if any.
    """

    content_type = ContentType.objects.get_for_model(model)

    return LogEntry.objects.filter(content_type=content_type, object_id=id)
