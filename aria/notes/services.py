from typing import Any

from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.db.models import Model

from aria.audit_logs.services import log_entries_create
from aria.audit_logs.types import ChangeMessage
from aria.core.services import model_update
from aria.notes.models import NoteEntry
from aria.notes.schemas.records import NoteEntryRecord
from aria.users.models import User


def note_entry_create(
    model: Model, *, obj_id: int, note: str, author: User
) -> NoteEntryRecord:
    """
    Create a new note instance.
    """

    content_type = ContentType.objects.get_for_model(model)

    if note is None:
        raise ValueError("Note cannot be empty!")

    created_note = NoteEntry.objects.create(
        author=author,
        content_type=content_type,
        object_id=obj_id,
        note=note,
    )

    return NoteEntryRecord(
        id=created_note.id,
        author_id=created_note.author_id if created_note.author_id else None,
        note=created_note.note,
    )


@transaction.atomic
def note_entry_update(
    note_id: int, author: User, data: Any, log_change: bool = True
) -> NoteEntryRecord:
    """
    Updates an existing note instance.
    """

    # Non side effect fields are field that does not have
    # any dependencies. E.g. fields that are not used in
    # the generation of for example other fields.
    non_side_effect_fields = ["author", "note"]

    note_instance = NoteEntry.objects.get(id=note_id)

    note_entry: NoteEntry
    has_updated: bool
    updated_fields: list[ChangeMessage]

    note_entry, has_updated, updated_fields = model_update(
        instance=note_instance, fields=non_side_effect_fields, data=data
    )

    if has_updated and author is not None and log_change:
        log_entries_create(
            author=author, instance=note_entry, change_messages=updated_fields
        )

    return NoteEntryRecord(
        id=note_entry.id, author_id=note_entry.author_id, note=note_entry.note
    )


def note_entry_delete(*, note_id: int) -> None:
    """
    Delete an existing note instance.
    """

    note = NoteEntry.objects.get(id=note_id)
    note.delete()
