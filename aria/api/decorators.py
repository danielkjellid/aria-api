import functools
from typing import Any, Callable, Optional, Union

from ninja import Router

from aria.api.responses import GenericResponse
from aria.core.exceptions import ApplicationError

SUPPORTED_HTTP_METHODS = ["GET", "POST", "DELETE", "PATCH", "PUT"]


def api(
    router: Router,
    path,
    *,
    method: SUPPORTED_HTTP_METHODS,
    response: Any,
    summary: Optional[str] = None,
    description: Optional[str] = None,
    url_name: Optional[str] = None,
) -> Callable[[Callable[..., Any]], Callable[..., GenericResponse]]:
    """
    Defines an API view. This is basically just a wrapper around Django
    Ninjas @router.method decorator, to throw a custom exception for all
    API views. The exceprion in question is raised in differenct services
    and selectors, and provides user feedback when something goes wrong.

    * router:
        This is the Django Ninja router defined in each respective viewset
        file. It's needed to append the correct views to the correct router.

    * path:
        The path of which are supposed to return the viewset.

    * method:
        HTTP method associated with the view. Since we want to follow the
        "one view does one thing"-logic, we only allow for a single method
        parameter at the time.

    * response:
        Response format as a pydantic model. Usually just GenerictResponse.

    * summary:
        Short summary about the viewset. For example "Creates a user". Will
        be displayed in OpenAPI docs.

    * description:
        Description about what the viewset/service in viewset does. Will be
        displayed in the OpenAPI docs.

    * url_name:
         Same as Django's name parameter in path. Used to reverse match urls
         in for example tests.
    """

    def decorator(func):
        # Get appropriate decorator based on router and method. This
        # is the same as doing @router.method(...) in the viewset.
        router_decorator = getattr(router, method.lower())

        router_tag = _get_and_validate_router_tag(router)
        formatted_path = path.replace("/", "-").rstrip("-")
        default_url_name = f"{router_tag}-{formatted_path}"

        @router_decorator(
            path,
            response=response,
            summary=summary,
            description=description,
            url_name=url_name if url_name else default_url_name,
        )
        @functools.wraps(func)
        def inner(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except ApplicationError:
                raise

        return inner

    return decorator


def _get_and_validate_router_tag(router: Router):
    """
    Check that there is only a single tag provided.
    """

    router_tag = router.tags

    if router_tag is None:
        raise NotImplementedError(
            'Router object must have a defined tag: Router(tags="...")'
        )

    if isinstance(router_tag, list):
        if len(router_tag) > 1:
            raise ValueError("Router object must only have one tag!")

        router_tag = router_tag[0]

    return router_tag
