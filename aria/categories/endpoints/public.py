from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from ninja import Router

from aria.categories.models import Category
from aria.categories.schemas.outputs import (
    CategoryChildrenListOutput,
    CategoryDetailOutput,
    CategoryListOutput,
    CategoryParentListOutput,
)
from aria.categories.selectors import (
    category_children_active_list_for_category,
    category_navigation_active_list_from_cache,
    category_parent_active_list,
)

router = Router(tags=["Categories"])


@router.get(
    "/",
    response={200: list[CategoryListOutput]},
    summary="List all active categories and children",
)
def category_list_api(request: HttpRequest) -> list[CategoryListOutput]:
    """
    Retrieves a list of all primary and secondary categories, primarily
    used for routing in the frontend navbar.
    """

    categories = category_navigation_active_list_from_cache()

    return [CategoryListOutput(**category.dict()) for category in categories]


@router.get(
    "parents/",
    response={200: list[CategoryParentListOutput]},
    summary="List all active primary categories",
)
def category_parent_list_api(request: HttpRequest) -> list[CategoryParentListOutput]:
    """
    Retrieves a list of all primary categories.
    """
    parent_categories = category_parent_active_list()

    return [
        CategoryParentListOutput(**category.dict()) for category in parent_categories
    ]


@router.get(
    "{category_slug}/",
    response={200: CategoryDetailOutput},
    summary="Retrieve a specific category",
)
def category_detail_api(
    request: HttpRequest, category_slug: str
) -> tuple[int, CategoryDetailOutput]:
    """
    Retrieve details of a specific category, parent
    or child.
    """
    category = get_object_or_404(Category, slug=category_slug)

    return 200, CategoryDetailOutput.from_orm(category)


@router.get(
    "{category_slug}/children/",
    response={200: list[CategoryChildrenListOutput]},
    summary="List all active children categories belonging to a parent",
)
def category_children_list_api(
    request: HttpRequest, category_slug: str
) -> list[CategoryChildrenListOutput]:
    """
    Retrieves a list of all children categories connected to a
    specific parent.
    """
    parent_category = get_object_or_404(Category, slug=category_slug)
    children_categories = category_children_active_list_for_category(
        category=parent_category
    )

    return [CategoryChildrenListOutput(**child.dict()) for child in children_categories]
