import json

from django.db import models
from django.contrib.postgres.fields import JSONField
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from users.models import User


class AuditLogManager(models.Manager):

    use_in_migration = True

    # constructor for creating a logging instance
    def log_update(self, user, content_type, object_id, content_object, change, date_of_change):

        return self.model.objects.create(
            user = user,
            content_type = content_type,
            object_id = object_id,
            content_object = content_object,
            change = change,
            date_of_change = date_of_change,
        )


class AuditLog(models.Model):
    user = models.ForeignKey(
        User, 
        related_name='changed_by', 
        on_delete = models.CASCADE
    )
    content_type = models.ForeignKey(
        ContentType, 
        models.SET_NULL, 
        verbose_name = _('content type'), 
        blank = True, 
        null = True,
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey(
        'content_type', 
        'object_id'
    )
    change = JSONField()
    date_of_change = models.DateTimeField(
        _('changed at'),
        default = timezone.now,
        editable = False
    )

    # add the auditlog model to the AuditLogManager
    objects = AuditLogManager()

    class Meta:
        verbose_name = _('Audit log entry')
        verbose_name_plural = _('Audit log entries')

    # method for creating an change message
    def create_log_entry(request, obj, old_instance):

        # get the new version of the instance by querying the object
        new_instance = obj.objects.get(pk = old_instance.pk)

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
                change_message = json.dumps({
                    'field': field.name,
                    'old_value': old_value,
                    'new_value': new_value
                })

                # use constructor created in manager to create a new model instance
                AuditLog.objects.log_update(
                    user = request,
                    content_type = ct,
                    content_object = new_instance,
                    object_id = new_instance.pk,
                    change = change_message,
                    date_of_change = timezone.now()
                )

    def get_logs(instance):

        ct = ContentType.objects.get_for_model(instance)

        return AuditLog.objects.filter(
            content_type = ct,
            object_id = instance.pk
        )

    
    #property to parse and return the changed JSON
    @cached_property
    # cached property is useful as it stops parsing the changes on every access
    def changes_dict(self):
        return json.loads(self.change)


class NoteManager(models.Manager):

    use_in_migration = True

    # constructor for creating a note instance
    def create_note_entry(self, user, content_type, object_id, content_object, note, created_at, updated_at):

        return self.model.objects.create(
            user = user,
            content_type = content_type,
            object_id = object_id,
            content_object = content_object,
            note = note,
            created_at = created_at,
            updated_at = updated_at,
        )


class Note(models.Model):
    user = models.ForeignKey(
        User,
        related_name='created_by',
        on_delete = models.CASCADE
    )
    content_type = models.ForeignKey(
        ContentType,
        models.SET_NULL,
        verbose_name = _('content type'),
        blank = True,
        null = True
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey(
        'content_type',
        'object_id'
    )
    note = models.TextField()
    created_at = models.DateTimeField(
        _('created at'),
        default = timezone.now
    )
    updated_at = models.DateTimeField(
        _('updated at'),
        default=timezone.now
    )

    objects = NoteManager()

    class Meta:
        verbose_name = _('Note')
        verbose_name_plural = _('Notes')
        permissions = (
            ('has_notes_add', 'Can add new notes'),
            ('has_note_edit', 'Can edit a single note instance'),
            ('has_note_delete', 'Can delete a single note instance')
        )

    def create_note(request, instance, note):

        # get content type for object to be able to edit correct instance
        ct = ContentType.objects.get_for_model(instance)

        # use constructor created in manager to create a new model instance
        Note.objects.create_note_entry(
            user = request,
            content_type = ct,
            content_object = instance,
            object_id = instance.pk,
            note = note,
            created_at = timezone.now(),
            updated_at = timezone.now()
        )

    def get_notes(instance):

        ct = ContentType.objects.get_for_model(instance)

        return Note.objects.filter(
            content_type = ct,
            object_id = instance.pk
        )

    def update_note(request, note_id, note):

        note_instance = Note.objects.get(pk = note_id)

        note_instance.note = note
        note_instance.user = request
        note_instance.updated_at = timezone.now()

        note_instance.save()

    def delete_note(note_id):
        
        note_instance = Note.objects.delete(pk=note_id)
        note_instance.delete()

