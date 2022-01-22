from typing import Union, List
from django.db.models import QuerySet, Model
from aria.audit_logs.models import LogEntry


def logs_get(*, instance: Model) -> Union[QuerySet, List[LogEntry]]:
    return LogEntry.get_logs(instance)
