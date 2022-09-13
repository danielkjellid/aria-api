from django.http import HttpRequest

from ninja import Router
from ninja.responses import codes_5xx

from aria.core.schemas.outputs import CoreSiteHealthOutput

router = Router(tags=["Core"])


@router.get(
    "health/",
    response={200: CoreSiteHealthOutput, codes_5xx: None},
    summary="Get api status",
)
def core_site_health_check_api(
    request: HttpRequest,
) -> tuple[int, CoreSiteHealthOutput]:
    """
    Returns ok if the site is not experiencing any issues. Used for
    measuring uptime during rolling deploys.
    """

    return 200, CoreSiteHealthOutput(status="ok")
