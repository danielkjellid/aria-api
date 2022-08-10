from django.http import HttpRequest

from ninja import Router

from aria.api.decorators import api
from aria.front.schemas.outputs import OpeningHoursOutputSchema, SiteMessageOutputSchema
from aria.front.selectors import (
    opening_hours_detail_from_cache,
    site_message_active_list_from_cache,
)

router = Router(tags=["Front"])


@api(
    router,
    "opening-hours/",
    method="GET",
    response={200: OpeningHoursOutputSchema},
    summary="Get opening hours for a site",
)
def opening_hours_detail_api(
    request: HttpRequest,
) -> tuple[int, OpeningHoursOutputSchema]:
    """
    Retrieve opening hours for a single site instance based on site id.
    """

    opening_hours = opening_hours_detail_from_cache()

    return 200, OpeningHoursOutputSchema(**opening_hours.dict())


@api(
    router,
    "site-messages/active/",
    method="GET",
    response={200: list[SiteMessageOutputSchema]},
    summary="Get site messages for a site",
)
def site_messages_active_list_api(
    request: HttpRequest,
) -> list[SiteMessageOutputSchema]:
    """
    Retrieve a list of active site messages for a specific site.
    """

    site_messages = site_message_active_list_from_cache()

    return [
        SiteMessageOutputSchema(**site_message.dict()) for site_message in site_messages
    ]
