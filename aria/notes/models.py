from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from aria.core.models import BaseModel
from aria.notes.managers import NoteEntryQuerySet
from aria.users.models import User

_NoteEntryManager = models.Manager.from_queryset(NoteEntryQuerySet)


class NoteEntry(BaseModel):
    author = models.ForeignKey(
        User, related_name="note_entries", on_delete=models.SET_NULL, null=True
    )
    content_type = models.ForeignKey(
        ContentType,
        models.SET_NULL,
        blank=True,
        null=True,
        related_name="notes",
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    note = models.TextField()

    objects = _NoteEntryManager()

    class Meta:
        verbose_name = "Note"
        verbose_name_plural = "Notes"
        permissions = (
            ("has_notes_list", "Can view notes"),
            ("has_notes_add", "Can add new notes"),
            ("has_note_edit", "Can edit a single note instance"),
            ("has_note_delete", "Can delete a single note instance"),
        )
