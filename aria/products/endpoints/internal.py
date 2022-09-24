from django.http import HttpRequest
from ninja import Router, Query, Schema

from aria.api.decorators import paginate
from aria.api.responses import codes_40x
from aria.api.schemas.responses import ExceptionResponse
from aria.api_auth.decorators import permission_required
from aria.products.enums import ProductStatus, ProductUnit
from aria.products.schemas.filters import ProductListFilters
from aria.products.schemas.outputs import ProductInternalListOutput
from aria.products.selectors.core import product_list
from aria.products.selectors.sizes import size_distinct_list
from aria.products.services import variant_create, size_create

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


class ProductCreateInternalInputFile(Schema):
    name: str
    file: str


class ProductCreateInternalInputImage(Schema):
    image: str


class ProductCreateInternalInputOption(Schema):
    variant_id: int | None
    size_id: int | None
    gross_price: float
    status: ProductStatus


class ProductCreateInternalInput(Schema):
    name: str
    status: ProductStatus
    slug: str
    thumbnail: str
    search_keywords: str
    description: str
    unit: ProductUnit
    vat_rate: float
    available_in_special_sizes: bool
    materials: list[str]
    rooms: list[str]
    absorption: float = None
    display_price: bool
    can_be_purchased_online: bool
    can_be_picked_up: bool

    # Relationships - should already exist.
    supplier_id: int
    category_ids: list[int]
    shape_ids: list[int]
    color_ids: list[int]

    # Relationships - needs creation.
    files: list[ProductCreateInternalInputFile]
    images: list[ProductCreateInternalInputImage]
    options: list[ProductCreateInternalInputOption]


@router.post(
    "create/",
    response={
        200: ProductCreateInternalInput,
        codes_40x: ExceptionResponse,
    },
)
def product_create_api(request: HttpRequest):
    pass


class VariantCreateInternalInput(Schema):
    name: str
    thumbnail: str | None


@router.post(
    "variants/create/",
    response={
        201: None,
        codes_40x: ExceptionResponse,
    },
    summary="Create a new variant.",
)
def variant_create_api(request: HttpRequest, payload: VariantCreateInternalInput):
    """
    Creates a single variant instance.
    """

    variant_create(**payload.dict())
    return 201


class SizeListInternalOutput(Schema):
    id: float | None
    width: float | None
    height: float | None
    depth: float | None
    circumference: float | None


@router.get(
    "sizes/",
    response={200: list[SizeListInternalOutput]},
    summary="List all distinct sizes.",
)
def size_list_api(request: HttpRequest) -> list[SizeListInternalOutput]:
    """
    Get a list of all distinct sizes in the application.
    """

    sizes = size_distinct_list()

    return [SizeListInternalOutput(**size.dict()) for size in sizes]


class SizeCreateInternalInput(Schema):
    width: float | None
    height: float | None
    depth: float | None
    circumference: float | None


@router.post(
    "sizes/create/",
    response={
        201: None,
        codes_40x: ExceptionResponse,
    },
    summary="Create a new size.",
)
def size_create_api(request: HttpRequest, payload: SizeCreateInternalInput) -> int:
    """
    Creates a single size instance if size does not already exist.
    """

    size_create(**payload.dict())
    return 201
