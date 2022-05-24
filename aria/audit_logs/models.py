import json

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property

from aria.audit_logs.managers import LogEntryQuerySet
from aria.users.models import User

_LogEntryManager = models.Manager.from_queryset(LogEntryQuerySet)


class LogEntry(models.Model):
    author = models.ForeignKey(
        User, related_name="log_entries", on_delete=models.SET_NULL, null=True
    )
    content_type = models.ForeignKey(
        ContentType,
        models.SET_NULL,
        verbose_name="content type",
        blank=True,
        null=True,
        related_name="logs",
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    change = models.JSONField()
    created_at = models.DateTimeField(
        "changed at", default=timezone.now, editable=False
    )

    objects = _LogEntryManager()

    class Meta:
        verbose_name = "Audit log entry"
        verbose_name_plural = "Audit log entries"
        permissions = (
            ("has_audit_logs_list", "Can view audit logs"),
            ("has_audit_logs_edit", "Can edit a single log instance"),
            ("has_audit_logs_delete", "Can delete a single log instance"),
        )

    # property to parse and return the changed JSON
    @cached_property  # cached property is useful as it stops parsing the changes on every access
    def changes_dict(self):
        return json.loads(self.change)
