from django.http import HttpRequest

from ninja import Router

from aria.front.schemas.outputs import OpeningHoursOutput, SiteMessageOutput
from aria.front.selectors import (
    opening_hours_detail_from_cache,
    site_message_active_list_from_cache,
)

router = Router(tags=["Front"])


@router.get(
    "opening-hours/",
    response={200: OpeningHoursOutput},
    summary="Get opening hours for a site",
)
def opening_hours_detail_api(
    request: HttpRequest,
) -> tuple[int, OpeningHoursOutput]:
    """
    Retrieve opening hours for a single site instance based on site id.
    """

    opening_hours = opening_hours_detail_from_cache()

    return 200, OpeningHoursOutput(**opening_hours.dict())


@router.get(
    "site-messages/active/",
    response={200: list[SiteMessageOutput]},
    summary="Get site messages for a site",
)
def site_messages_active_list_api(
    request: HttpRequest,
) -> list[SiteMessageOutput]:
    """
    Retrieve a list of active site messages for a specific site.
    """

    site_messages = site_message_active_list_from_cache()

    return [SiteMessageOutput(**site_message.dict()) for site_message in site_messages]
