import json

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from aria.audit_logs.managers import LogEntryManager
from aria.users.models import User


class LogEntry(models.Model):
    author = models.ForeignKey(
        User, related_name="log_entries", on_delete=models.CASCADE
    )
    content_type = models.ForeignKey(
        ContentType,
        models.SET_NULL,
        verbose_name=_("content type"),
        blank=True,
        null=True,
        related_name="logs",
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    change = models.JSONField()
    date_of_change = models.DateTimeField(
        _("changed at"), default=timezone.now, editable=False
    )

    # add the auditlog model to the LogEntryManager
    objects = LogEntryManager()

    class Meta:
        verbose_name = _("Audit log entry")
        verbose_name_plural = _("Audit log entries")
        permissions = (
            ("has_audit_logs_list", "Can view audit logs"),
            ("has_audit_logs_edit", "Can edit a single log instance"),
            ("has_audit_logs_delete", "Can delete a single log instance"),
        )

    # property to parse and return the changed JSON
    @cached_property
    # cached property is useful as it stops parsing the changes on every access
    def changes_dict(self):
        return json.loads(self.change)
