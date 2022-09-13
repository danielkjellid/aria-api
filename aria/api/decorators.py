from functools import partial, wraps
from functools import partial, wraps
from typing import Any, Callable, Tuple

from ninja.compatibility.util import get_args as get_collection_args
from ninja.constants import NOT_SET
from ninja.errors import ConfigError
from ninja.operation import Operation
from ninja.signature.details import is_collection_type
from ninja.types import DictStrAny

from aria.api.pagination import PageNumberSetPagination

SUPPORTED_HTTP_METHODS = ["GET", "POST", "DELETE", "PATCH", "PUT"]


def paginate(**paginator_params: Any) -> Callable[[Callable[..., Any]], Any]:
    """
    Paginate a response.

    @api(...)
    @paginate(page_size=n)
    def my_view(request):
    """

    def wrapper(func: Callable[..., Any]) -> Callable[..., Any]:
        return _inject_pagination(func, **paginator_params)

    return wrapper


def _inject_pagination(
    func: Callable[..., Any],
    **paginator_params: Any,
) -> Callable[[Callable[..., Any]], Any]:
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
        if paginator.Output:  # pylint: disable=using-constant-test
            result["data"] = list(result["data"])
        return result

    view_with_pagination._ninja_contribute_args = [  # type: ignore
        (
            "ninja_pagination",
            paginator.Input,
            paginator.InputSource,
        ),
    ]

    if paginator.Output:  # pylint: disable=using-constant-test
        view_with_pagination._ninja_contribute_to_operation = partial(  # type: ignore
            make_response_paginated, paginator
        )

    return view_with_pagination  # type: ignore


def make_response_paginated(paginator: PageNumberSetPagination, op: Operation) -> None:
    """
    Takes operation response and changes it to the paginated response
    for example:
        response=List[Some]
    will be changed to:
        response=PagedSome
    where Paged some will be a subclass of paginator.Output:
        class PagedSome:
            items: List[Some]
            count: int
    """
    status_code, item_schema = _find_collection_response(op)

    # Switching schema to Output schema
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

    # changing response model to newly created one
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
