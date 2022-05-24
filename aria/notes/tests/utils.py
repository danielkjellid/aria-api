from django.contrib.contenttypes.models import ContentType
from django.db.models import Model

from aria.notes.models import NoteEntry
from aria.users.models import User


def create_note_entry(
    model: Model, *, id: int, author: User, note: str = "This is a test note"
) -> NoteEntry:
    content_type = ContentType.objects.get_for_model(model)
    note_entry = NoteEntry.objects.create(
        author=author, content_type=content_type, object_id=id, note=note
    )

    return note_entry
