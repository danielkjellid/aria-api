from django.http import HttpRequest
from django.shortcuts import get_object_or_404

from ninja import Query, Router

from aria.api.decorators import api
from aria.categories.models import Category
from aria.core.exceptions import ApplicationError
from aria.products.schemas.filters import ProductListFilters
from aria.products.schemas.outputs import ProductDetailOutput, ProductListOutput
from aria.products.selectors import product_detail, product_list_by_category_from_cache

router = Router(tags=["Products"])


@api(
    router,
    "category/{category_slug}/",
    method="GET",
    response={200: list[ProductListOutput]},
    summary="List all products belonging to a certain category",
)
def product_list_by_category_api(
    request: HttpRequest, category_slug: str, search: ProductListFilters = Query(...)
) -> list[ProductListOutput]:
    """
    Get a list of products related to a specific category.
    """

    category = get_object_or_404(Category, slug=category_slug)
    products = product_list_by_category_from_cache(
        category=category, filters=search.dict()
    )

    return [ProductListOutput(**product.dict()) for product in products]


@api(
    router,
    "product/{product_slug}/",
    method="GET",
    response={200: ProductDetailOutput},
    summary="Get information about a single product instance",
)
def product_detail_api(
    request: HttpRequest, product_slug: str
) -> tuple[int, ProductDetailOutput]:
    """
    Retrieve a single product instance based on product slug.
    """

    product = product_detail(product_slug=product_slug)

    if product is None:
        raise ApplicationError(
            "Product with provided slug does not exist", status_code=404
        )

    return 200, ProductDetailOutput(**product.dict())
