from ninja import Router

from aria.api.decorators import api
from aria.categories.schemas.outputs import CategoryListOutput
from aria.categories.selectors import categories_navigation_active_list

router = Router(tags="categories")


@api(
    router,
    "/",
    method="GET",
    response={200: list[CategoryListOutput]},
    summary="List all categories and children",
)
def category_list_api(request):
    """
    Endpoint to fetch categories used for routing
    in the frontend navbar.
    """

    categories = categories_navigation_active_list()

    return categories


def category_parent_list_api(request):
    pass


def category_children_list_api(request):
    pass


def category_products_list_api(request):
    pass


def category_detail_api(request):
    pass
