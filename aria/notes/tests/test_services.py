import pytest

from aria.audit_logs.selectors import log_list_for_instance
from aria.notes.models import NoteEntry
from aria.notes.services import note_entry_create, note_entry_delete, note_entry_update
from aria.notes.tests.utils import create_note_entry
from aria.users.models import User
from aria.users.tests.utils import create_user

pytestmark = pytest.mark.django_db


class TestNotesServices:
    def test_note_entry_create(self, django_assert_max_num_queries, unprivileged_user):
        """
        Test that the note_entry_create service creates a note entry.
        """

        user = create_user()
        author = create_user(email="author@example.com")

        # Test that ValueError is raised if note is None
        with pytest.raises(ValueError):
            note_entry_create(User, id=user.id, author=author, note=None)

        assert NoteEntry.objects.count() == 0

        # Uses 1 query to create note entry.
        with django_assert_max_num_queries(1):
            created_note = note_entry_create(
                User, id=user.id, author=author, note="Test note"
            )

        assert NoteEntry.objects.count() == 1
        assert NoteEntry.objects.filter(id=created_note.id).exists()
        assert created_note.author_id == author.id
        assert created_note.note == "Test note"

    def test_note_entry_update(self, django_assert_max_num_queries):
        """
        Test that the note_entry_update service updates a note entry
        and creates appropriate logs.
        """

        user = create_user()
        author = create_user(email="author@example.com")
        note = create_note_entry(User, id=user.id, author=author, note="User note")

        # Save "old" field to assert later.
        old_note_content = note.note

        updates = {"note": "Updated user note"}

        # Uses 8 queries:
        # - 2 atomic transaction, creates an releases savepoint
        # - 1 Get note based on note id
        # - 1 Get author
        # - 1 Get content type
        # - 1 Update note
        # - 1 Get content type for log
        # - 1 Add log
        with django_assert_max_num_queries(8):
            updated_note = note_entry_update(
                note_id=note.id, author=author, data=updates, log_change=True
            )

        created_log_entry = log_list_for_instance(NoteEntry, id=updated_note.id)[0]

        assert updated_note.note == "Updated user note"

        # Assert that we didn't change any other data
        assert updated_note.author_id == author.id

        # Assert correct log entry
        assert created_log_entry.change["old_value"] == old_note_content
        assert created_log_entry.change["new_value"] == updated_note.note

    def test_note_entry_delete(self, django_assert_max_num_queries):
        """
        Test that the note_entry_delete service delete a note entry
        based on provided id.
        """

        user = create_user()
        author = create_user(email="author@example.com")
        note = create_note_entry(User, id=user.id, author=author, note="User note")

        # Test that we raise exception if id does not exist.
        with pytest.raises(NoteEntry.DoesNotExist):
            note_entry_delete(id=999)

        assert NoteEntry.objects.count() == 1

        # Uses 2 queries: 1 for getting note, and 1 for deleting it.
        with django_assert_max_num_queries(2):
            note_entry_delete(id=note.id)

        # Assert that note is actually deleted.
        assert NoteEntry.objects.count() == 0
        assert not NoteEntry.objects.filter(id=note.id).exists()
