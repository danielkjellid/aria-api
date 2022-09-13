from django.http import HttpRequest

from ninja import Router

from aria.api_auth.decorators import permission_required
from aria.notes.services import note_entry_delete

router = Router(tags=["Notes"])


@router.delete(
    "{note_id}/delete/", response={200: None}, summary="Delete a specific note instance"
)
@permission_required("notes.has_note_delete")
def note_delete_api(request: HttpRequest, note_id: int) -> tuple[int, None]:
    """
    Delete a specific note instance based on provided id.
    """

    note_entry_delete(note_id=note_id)
    return 200, None
