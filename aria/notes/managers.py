from django.db import models


class NoteManager(models.Manager):

    use_in_migration = True

    # constructor for creating a note instance
    def create_note_entry(
        self,
        user,
        content_type,
        object_id,
        content_object,
        note,
        created_at,
        updated_at,
    ):

        return self.model.objects.create(
            user=user,
            content_type=content_type,
            object_id=object_id,
            content_object=content_object,
            note=note,
            created_at=created_at,
            updated_at=updated_at,
        )
