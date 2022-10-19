from django.http import HttpRequest

from ninja import Router, Schema

from aria.api.responses import codes_40x
from aria.api.schemas.responses import ExceptionResponse
from aria.categories.selectors import category_children_list

router = Router(tags=["Categories"])


class CategoryListInternalOutput(Schema):
    id: int
    name: str
    display_name: str


@router.get(
    "/",
    response={200: list[CategoryListInternalOutput], codes_40x: ExceptionResponse},
    summary="List all categories.",
    url_name="internal-categories-index",  # Temporary.
)
def category_list_internal_api(request: HttpRequest):
    """
    Endpoint for getting a list of all categories in the application.
    """

    categories = category_children_list()

    return [CategoryListInternalOutput(**category.dict()) for category in categories]
