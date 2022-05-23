from django.utils.translation import gettext as _

from ninja import Router

from aria.api.decorators import api
from aria.core.exceptions import ApplicationError
from aria.kitchens.schemas.outputs import KitchenDetailOutput, KitchenListOutput
from aria.kitchens.selectors import kitchen_available_list, kitchen_detail

router = Router(tags="kitchens")


@api(
    router,
    "/",
    method="GET",
    response={200: list[KitchenListOutput]},
    summary="List all available kitchens",
)
def kitchen_list_api(request):
    """
    Retrieves a list of all kitchens with status available.
    """

    available_kitchens = kitchen_available_list()

    return available_kitchens


@api(
    router,
    "kitchen/{kitchen_slug}/",
    method="GET",
    response={200: KitchenDetailOutput},
    summary="Get information about a single kitchen instance",
)
def kitchen_detail_api(request, kitchen_slug: str):
    """
    Retrieve a single kitchen instance based on kitchen slug.
    """

    kitchen = kitchen_detail(kitchen_slug=kitchen_slug)

    if kitchen is None:
        raise ApplicationError(
            _("Kitchen with provided slug does not exist"), status_code=404
        )

    return 200, kitchen
