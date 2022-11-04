from typing import TYPE_CHECKING

from aria.core.managers import BaseQuerySet

if TYPE_CHECKING:
    from aria.audit_logs import models  # noqa


class LogEntryQuerySet(BaseQuerySet["models.LogEntry"]):
    pass
