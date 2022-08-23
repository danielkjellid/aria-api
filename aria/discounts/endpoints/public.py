from django.http import HttpRequest

from ninja import Router

from aria.api.decorators import api
from aria.discounts.schemas.outputs import DiscountsActiveListOutput
from aria.discounts.selectors import discount_active_list_from_cache

router = Router(tags=["Discounts"])


@api(
    router,
    "active/",
    method="GET",
    response={200: list[DiscountsActiveListOutput]},
    summary="List all active discounts",
)
def discount_active_list_api(request: HttpRequest) -> list[DiscountsActiveListOutput]:
    """
    Retrieve a list of currently active discounts.
    """

    active_discounts = discount_active_list_from_cache()

    return [
        DiscountsActiveListOutput(**discount.dict()) for discount in active_discounts
    ]
