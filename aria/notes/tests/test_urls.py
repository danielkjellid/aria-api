from django.urls import reverse


class TestPublicNotesUrls:
    pass


class TestInternalNotesUrls:
    def test_url_note_delete_api(self) -> None:
        """
        Test reverse match of note_delete_api endpoint.
        """
        url = reverse(
            "api-internal-1.0.0:notes-note-{note_id}-delete", args=["note_id"]
        )

        assert url == "/api/v1/internal/notes/note/note_id/delete/"
