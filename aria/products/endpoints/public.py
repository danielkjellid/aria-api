from django.utils.translation import gettext as _

from ninja import Router

from aria.api.decorators import api
from aria.core.exceptions import ApplicationError
from aria.products.schemas.outputs import ProductDetailOutput
from aria.products.selectors import product_detail

router = Router(tags=["Products"])


@api(
    router,
    "product/{product_slug}/",
    method="GET",
    response={200: ProductDetailOutput},
    summary="Get information about a single product instance",
)
def product_detail_api(request, product_slug: str) -> tuple[int, ProductDetailOutput]:
    """
    Retrieve a single product instance based on product slug.
    """

    product = product_detail(product_slug=product_slug)

    if product is None:
        raise ApplicationError(
            _("Product with provided slug does not exist"), status_code=404
        )

    return 200, product
