from ninja import Router
from ninja.responses import codes_5xx

from aria.api.decorators import api
from aria.core.schemas.outputs import CoreSiteHealthOutput

router = Router(tags=["Core"])


@api(
    router,
    "health/",
    method="GET",
    response={200: CoreSiteHealthOutput, codes_5xx: None},
    summary="Get api status",
)
def core_site_health_check_api(request):
    """
    Returns ok if the site is not experiencing any issues. Used for
    meausuring uptime during rolling deploys.
    """

    return 200, CoreSiteHealthOutput(status="ok")
