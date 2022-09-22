from django.http import HttpRequest
from ninja import Router, Query

from aria.api.decorators import paginate
from aria.api.responses import codes_40x
from aria.api.schemas.responses import ExceptionResponse
from aria.api_auth.decorators import permission_required
from aria.products.schemas.filters import ProductListFilters
from aria.products.schemas.outputs import ProductInternalListOutput
from aria.products.selectors import product_list

router = Router(tags=["Products"])


@router.get(
    "/",
    response={
        200: list[ProductInternalListOutput],
        codes_40x: ExceptionResponse,
    },
    summary="List all products",
)
@paginate(page_size=50)
@permission_required("products.has_products_list")
def product_list_internal_api(
    request: HttpRequest, filters: ProductListFilters = Query(...)
) -> list[ProductInternalListOutput]:
    """
    Retrieve a list of all products in the application.
    """

    products = product_list(filters=filters.dict())
    return [ProductInternalListOutput(**product.dict()) for product in products]
