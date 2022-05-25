from ninja import Router

from aria.api.decorators import api
from aria.api_auth.decorators import permission_required
from aria.notes.services import note_entry_delete

router = Router(tags=["Notes"])


@api(
    router,
    "note/{note_id}/delete/",
    method="DELETE",
    response={200: None},
    summary="Delete a specific note instance",
)
@permission_required("notes.has_note_delete")
def note_delete_api(request, note_id: int):
    """
    Delete a specific note instance based on provided id.
    """

    note_entry_delete(id=note_id)
    return 200, None
