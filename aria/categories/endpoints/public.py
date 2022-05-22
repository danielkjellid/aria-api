from ninja import Router

from aria.api.decorators import api
from aria.categories.schemas.outputs import CategoryListOutput, CategoryParentListOutput
from aria.categories.selectors import (
    categories_navigation_active_list,
    categories_parent_active_list,
)

router = Router(tags="categories")


@api(
    router,
    "/",
    method="GET",
    response={200: list[CategoryListOutput]},
    summary="List all active categories and children",
)
def category_list_api(request):
    """
    Retrieves a list of all primary and secondary categories, primarily
    used for routing in the frontend navbar.
    """

    categories = categories_navigation_active_list()

    return categories


@api(
    router,
    "parents/",
    method="GET",
    response={200: list[CategoryParentListOutput]},
    summary="List all active primary categories",
)
def category_parent_list_api(request):
    """
    Retrives a list of all primary categories.
    """
    parent_categories = categories_parent_active_list()

    return parent_categories


def category_children_list_api(request):
    pass


def category_products_list_api(request):
    pass


def category_detail_api(request):
    pass
