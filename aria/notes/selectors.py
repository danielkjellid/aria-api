from django.contrib.contenttypes.models import ContentType
from django.db.models import Model

from aria.notes.models import NoteEntry
from aria.notes.schemas.records import NoteEntryRecord


def note_entry_list_for_instance(model: Model, *, obj_id: int) -> list[NoteEntryRecord]:
    """
    Generic get service meant to be reused in local get services
    For example:

    def user_notes_list(user_id: int) -> list[NoteEntryRecord]:
        return note_entry_list_for_instance(User, id=user_id)

    Return value: List of NoteEntryRecords belloning to instance, if any.
    """

    content_type = ContentType.objects.get_for_model(model)
    notes = (
        NoteEntry.objects.filter(content_type=content_type, object_id=obj_id)
        .prefetch_related("author", "content_object")
        .order_by("-created_at")
    )

    return [
        NoteEntryRecord(id=note.id, author_id=note.author_id, note=note.note)
        for note in notes
    ]
