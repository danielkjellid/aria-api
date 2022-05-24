import pytest

from aria.notes.models import NoteEntry
from aria.notes.tests.utils import create_note_entry
from aria.users.models import User
from aria.users.tests.utils import create_user

pytestmark = pytest.mark.django_db


class TestPublicNotesEndpoints:
    pass


class TestPrivateNotesEndpoints:

    BASE_ENDPOINT = "/api/notes"

    def test_anonymous_client_note_delete_api(
        self, anonymous_client, django_assert_max_num_queries
    ):
        """
        Test that unauthenticated users gets a 401 unauthorized on deleting
        notes.
        """

        user = create_user()
        author = create_user(email="author@example.com")
        note = create_note_entry(User, id=user.id, author=author, note="Test note")

        with django_assert_max_num_queries(0):
            response = anonymous_client.delete(
                f"{self.BASE_ENDPOINT}/note/{note.id}/delete/"
            )

        assert response.status_code == 401

    def test_authenticated_unprivileged_client_note_delete_api(
        self, n_authenticated_unprivileged_client, django_assert_max_num_queries
    ):
        """
        Test that authenticated, unprivileged, users gets a 403 forbidden on
        deleting notes.
        """

        user = create_user()
        author = create_user(email="author@example.com")
        note = create_note_entry(User, id=user.id, author=author, note="Test note")

        # Uses 3 queries: 1 for getting the user, 2 for checking permissions.
        with django_assert_max_num_queries(3):
            response = n_authenticated_unprivileged_client.delete(
                f"{self.BASE_ENDPOINT}/note/{note.id}/delete/"
            )

        assert response.status_code == 403

    @pytest.mark.parametrize("test_permissions", ["has_note_delete"], indirect=True)
    def test_authenticated_privileged_client_note_delete_api(
        self, n_authenticated_privileged_client, django_assert_max_num_queries
    ):
        """
        Test that privileged users gets a valid response on deleting notes.
        """

        user = create_user()
        author = create_user(email="author@example.com")
        note = create_note_entry(User, id=user.id, author=author, note="Test note")

        assert NoteEntry.objects.count() == 1

        # Uses 5 queries: 1 for getting the user, 2 for checking permissions,
        # 1 for getting note and 1 for deleting note.
        with django_assert_max_num_queries(5):
            response = n_authenticated_privileged_client.delete(
                f"{self.BASE_ENDPOINT}/note/{note.id}/delete/"
            )

        assert response.status_code == 200
        assert NoteEntry.objects.count() == 0
        assert not NoteEntry.objects.filter(id=note.id).exists()
