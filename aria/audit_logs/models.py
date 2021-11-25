import json

from django.db import models
from django.contrib.postgres.fields import JSONField
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from aria.audit_logs.managers import LogEntryManager

from aria.users.models import User


class LogEntry(models.Model):
    user = models.ForeignKey(User, related_name="log_entries", on_delete=models.CASCADE)
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

    # method for creating an change message
    def create_log_entry(request, obj, old_instance):

        # get the new version of the instance by querying the object
        new_instance = obj.objects.get(pk=old_instance.pk)

        # get content type for object
        ct = ContentType.objects.get_for_model(new_instance)

        # loop for checking fields on the old instance and compare it to the new one
        for field in obj._meta.get_fields():

            # filter out reverse relations to prevent typerror
            if isinstance(field, models.ManyToOneRel):
                continue

            # get the value of old and new fields
            old_value = getattr(old_instance, field.name)
            new_value = getattr(new_instance, field.name)

            # check if old does not match new
            if old_value != new_value:
                # print('After check')

                # format changemessage as JSON
                change_message = {
                    "field": field.name,
                    "old_value": old_value,
                    "new_value": new_value,
                }

                # use constructor created in manager to create a new model instance
                LogEntry.objects.log_update(
                    user=request,
                    content_type=ct,
                    content_object=new_instance,
                    object_id=new_instance.pk,
                    change=change_message,
                    date_of_change=timezone.now(),
                )

    def get_logs(instance):

        ct = ContentType.objects.get_for_model(instance)

        return LogEntry.objects.filter(content_type=ct, object_id=instance.pk).order_by(
            "-date_of_change"
        )

    # property to parse and return the changed JSON
    @cached_property
    # cached property is useful as it stops parsing the changes on every access
    def changes_dict(self):
        return json.loads(self.change)
