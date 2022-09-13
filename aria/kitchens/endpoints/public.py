from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _
from ninja import Router

from aria.kitchens.schemas.outputs import KitchenDetailOutput, KitchenListOutput
from aria.kitchens.selectors import kitchen_available_list, kitchen_detail

router = Router(tags=["Kitchens"])


@router.get(
    "/", response={200: list[KitchenListOutput]}, summary="List all available kitchens"
)
def kitchen_list_api(request: HttpRequest) -> list[KitchenListOutput]:
    """
    Retrieves a list of all kitchens with status available.
    """

    available_kitchens = kitchen_available_list()

    return [KitchenListOutput(**kitchen.dict()) for kitchen in available_kitchens]


@router.get(
    "{kitchen_slug}/",
    response={200: KitchenDetailOutput},
    summary="Get information about a single kitchen instance",
)
def kitchen_detail_api(
    request: HttpRequest, kitchen_slug: str
) -> tuple[int, KitchenDetailOutput]:
    """
    Retrieve a single kitchen instance based on kitchen slug.
    """

    kitchen = kitchen_detail(kitchen_slug=kitchen_slug)

    if kitchen is None:
        raise ObjectDoesNotExist(_("Kitchen does not exist"))

    return 200, KitchenDetailOutput(**kitchen.dict())
