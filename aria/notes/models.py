from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from aria.notes.managers import NoteManager

from aria.users.models import User


class NoteEntry(models.Model):
    user = models.ForeignKey(
        User, related_name="note_entries", on_delete=models.CASCADE
    )
    content_type = models.ForeignKey(
        ContentType,
        models.SET_NULL,
        verbose_name=_("content type"),
        blank=True,
        null=True,
        related_name="notes",
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    note = models.TextField()
    created_at = models.DateTimeField(_("created at"), default=timezone.now)
    updated_at = models.DateTimeField(_("updated at"), default=timezone.now)

    objects = NoteManager()

    class Meta:
        verbose_name = _("Note")
        verbose_name_plural = _("Notes")
        permissions = (
            ("has_notes_add", "Can add new notes"),
            ("has_note_edit", "Can edit a single note instance"),
            ("has_note_delete", "Can delete a single note instance"),
        )

    def create_note(request, instance, note):

        # get content type for object to be able to edit correct instance
        ct = ContentType.objects.get_for_model(instance)

        # use constructor created in manager to create a new model instance
        NoteEntry.objects.create_note_entry(
            user=request,
            content_type=ct,
            content_object=instance,
            object_id=instance.pk,
            note=note,
            created_at=timezone.now(),
            updated_at=timezone.now(),
        )

    def get_notes(instance):

        ct = ContentType.objects.get_for_model(instance)

        return NoteEntry.objects.filter(content_type=ct, object_id=instance.pk)

    def update_note(request, note_id, note):

        note_instance = NoteEntry.objects.get(pk=note_id)

        note_instance.note = note
        note_instance.user = request
        note_instance.updated_at = timezone.now()

        note_instance.save()

    def delete_note(note_id):

        note_instance = NoteEntry.objects.get(pk=note_id)
        note_instance.delete()
