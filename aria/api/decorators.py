import functools
from functools import partial, wraps
from typing import Any, Callable, Optional, Tuple

from ninja import Router
from ninja.compatibility.util import get_args as get_collection_args
from ninja.constants import NOT_SET
from ninja.errors import ConfigError
from ninja.operation import Operation
from ninja.signature.details import is_collection_type
from ninja.types import DictStrAny

from aria.api.pagination import PageNumberSetPagination
from aria.api.schemas.responses import APIResponse
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
    **kwargs: Any,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
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

        default_url_name = url_name
        if default_url_name is None:
            router_tag = _get_and_validate_router_tag(router)
            formatted_path = path.replace("/", "-").rstrip("-")
            default_url_name = f"{router_tag}-{formatted_path}"

            # If the name ends with a "-", it means that we're dealing
            # with an index, in that case, add a trailing index to it.
            if default_url_name.endswith("-"):
                default_url_name = f"{default_url_name}index"

        @router_decorator(
            path,
            response=response,
            summary=summary,
            description=description if description else None,
            url_name=default_url_name,
            **kwargs,
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


def paginate(**paginator_params: DictStrAny) -> Callable:
    """
    Paginate a response.

    @api(...)
    @paginage(page_size=n)
    def my_view(request):
    """

    def wrapper(func: Callable) -> Any:
        return _inject_pagination(func, **paginator_params)

    return wrapper


def _inject_pagination(
    func: Callable,
    **paginator_params: Any,
) -> Callable:
    """
    This utility is basically just copied from django ninja to
    inject the request in the paginator, so that it can be used
    for url/url resolving.
    """

    paginator = PageNumberSetPagination(**paginator_params)

    @wraps(func)
    def view_with_pagination(*args: Tuple[Any], **kwargs: DictStrAny) -> Any:
        pagination_params = kwargs.pop("ninja_pagination")

        *_, request = args

        # Add request to paginator.
        paginator.request = request

        if paginator.pass_parameter:
            kwargs[paginator.pass_parameter] = pagination_params

        items = func(*args, **kwargs)

        result = paginator.paginate_queryset(
            items, pagination=pagination_params, **kwargs
        )
        if paginator.Output:
            result["data"] = list(result["data"])
        return result

    view_with_pagination._ninja_contribute_args = [  # type: ignore
        (
            "ninja_pagination",
            paginator.Input,
            paginator.InputSource,
        ),
    ]

    if paginator.Output:
        view_with_pagination._ninja_contribute_to_operation = partial(  # type: ignore
            make_response_paginated, paginator
        )

    return view_with_pagination


def make_response_paginated(paginator: PageNumberSetPagination, op: Operation) -> None:
    """
    Takes operation response and changes it to the paginated response
    for example:
        response=List[Some]
    will be changed to:
        response=PagedSome
    where Paged some willbe a subclass of paginator.Output:
        class PagedSome:
            items: List[Some]
            count: int
    """
    status_code, item_schema = _find_collection_response(op)

    # Swithcing schema to Output shcema
    try:
        new_name = f"Paged{item_schema.__name__}"
    except AttributeError:
        new_name = f"Paged{str(item_schema).replace('.', '_')}"  # typing.Any case

    new_schema = type(
        new_name,
        (paginator.Output,),
        {
            "__annotations__": {"data": list[item_schema]},  # type: ignore
            "data": [],
        },
    )  # typing: ignore

    response = op._create_response_model(new_schema)

    # chaging response model to newly created one
    op.response_models[status_code] = response


def _find_collection_response(op: Operation) -> Tuple[int, Any]:
    for code, resp_model in op.response_models.items():
        if resp_model is None or resp_model is NOT_SET:
            continue

        model = resp_model.__annotations__["response"]
        if is_collection_type(model):
            item_schema = get_collection_args(model)[0]
            return code, item_schema

    raise ConfigError(
        f'"{op.view_func}" has no collection response (e.g. response=List[SomeSchema])'
    )
