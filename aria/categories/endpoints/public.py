from django.shortcuts import get_object_or_404

from ninja import Query, Router

from aria.api.decorators import api
from aria.categories.models import Category
from aria.categories.schemas.filters import CategoryProductListFilters
from aria.categories.schemas.outputs import (
    CategoryChildrenListOutput,
    CategoryDetailOutput,
    CategoryListOutput,
    CategoryParentListOutput,
    CategoryProductListOutput,
)
from aria.categories.selectors import (
    categories_children_active_list_for_category,
    categories_navigation_active_list,
    categories_parent_active_list,
    category_related_product_list_by_category,
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


@api(
    router,
    "category/{category_slug}/",
    method="GET",
    response={200: CategoryDetailOutput},
    summary="Retrieve a specific category",
)
def category_detail_api(request, category_slug: str):
    """
    Retrieve details of a specific category, parent
    or child.
    """
    category = get_object_or_404(Category, slug=category_slug)

    return 200, category


@api(
    router,
    "category/{category_slug}/children/",
    method="GET",
    response={200: list[CategoryChildrenListOutput]},
    summary="List all active children categories bellonging to a parent",
)
def category_children_list_api(request, category_slug: str):
    """
    Retrives a list of all choldren categories connected to a
    specific parent.
    """
    parent_category = get_object_or_404(Category, slug=category_slug)
    children_categories = categories_children_active_list_for_category(
        category=parent_category
    )

    return children_categories


@api(
    router,
    "category/{category_slug}/products/",
    method="GET",
    response={200: list[CategoryProductListOutput]},
    summary="List all active children categories bellonging to a parent",
)
def category_products_list_api(
    request, category_slug: str, search: CategoryProductListFilters = Query(...)
):
    """
    Get a list of products related to a specific category.
    """
    category = get_object_or_404(Category, slug=category_slug)
    products = category_related_product_list_by_category(
        category=category, filters=search.dict()
    )

    return products
