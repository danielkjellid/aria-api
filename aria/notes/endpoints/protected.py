from ninja import Router

from aria.api.decorators import api
from aria.api_auth.decorators import permission_required

router = Router(tags="notes")


@api(
    router,
    "/note/{note_id}/delete/",
    method="DELETE",
    response={200: None},
    summary="Delete a specific note instance",
)
@permission_required("notes.has_note_delete")
def note_delete_api(request, note_id: int):
    pass
