from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from ninja import Router, Query, Schema, Form, UploadedFile, File

from aria.api.decorators import paginate
from aria.api.responses import codes_40x
from aria.api.schemas.responses import ExceptionResponse
from aria.api_auth.decorators import permission_required
from aria.products.enums import ProductStatus, ProductUnit
from aria.products.models import Product
from aria.products.schemas.filters import ProductListFilters
from aria.products.schemas.outputs import ProductInternalListOutput
from aria.products.selectors.core import product_list
from aria.products.selectors.sizes import size_distinct_list
from aria.products.selectors.variants import variant_list
from aria.products.services import (
    variant_create,
    size_get_or_create,
    product_file_create,
    product_option_create,
)

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


class ProductFileCreateInternalInput(Schema):
    name: str


class ProductFileCreateInternalOutput(Schema):
    product_id: int
    name: str
    file: str | None


@router.post(
    "{product_id}/files/create/",
    response={
        201: ProductFileCreateInternalOutput,
        codes_40x: ExceptionResponse,
    },
    summary="Create a file associated to a product.",
)
def product_file_create_api(
    request: HttpRequest,
    product_id: int,
    payload: ProductFileCreateInternalInput = Form(...),
    file: UploadedFile = File(...),
):
    """
    Create a file associated to a certain product based on a product's id.
    """

    product = get_object_or_404(Product, pk=product_id)
    product_file = product_file_create(product=product, name=payload.name, file=file)

    return 201, ProductFileCreateInternalOutput(
        product_id=product_file.product.id,
        name=product_file.name,
        file=product_file.file.url if product_file.file else None,
    )


class VariantListInternalOutput(Schema):
    id: int
    name: str
    is_standard: bool
    image: str | None
    thumbnail: str | None


@router.get(
    "variants/",
    response={
        200: list[VariantListInternalOutput],
        codes_40x: ExceptionResponse,
    },
    summary="List all variants.",
)
def variant_list_internal_api(request: HttpRequest) -> list[VariantListInternalOutput]:
    """
    Get a list of all variants in the application.
    """

    variants = variant_list()

    return [VariantListInternalOutput(**variant.dict()) for variant in variants]


class VariantCreateInternalInput(Schema):
    name: str
    is_standard: bool


class VariantCreateInternalOutput(Schema):
    id: int
    name: str
    is_standard: bool
    image: str | None
    thumbnail: str | None


@router.post(
    "variants/create/",
    response={
        201: VariantCreateInternalOutput,
        codes_40x: ExceptionResponse,
    },
    summary="Create a new variant.",
)
def variant_create_internal_api(
    request: HttpRequest,
    payload: VariantCreateInternalInput = Form(...),
    file: UploadedFile = File(...),
):
    """
    Creates a single variant instance.
    """

    variant = variant_create(
        name=payload.name, is_standard=payload.is_standard, thumbnail=file
    )

    return 201, VariantCreateInternalOutput(
        id=variant.id,
        name=variant.name,
        is_standard=variant.is_standard,
        image=variant.image.url if variant.image else None,
        thumbnail=variant.thumbnail.url if variant.thumbnail else None,
    )


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
def size_list_internal_api(request: HttpRequest) -> list[SizeListInternalOutput]:
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
def size_create_internal_api(
    request: HttpRequest, payload: SizeCreateInternalInput
) -> int:
    """
    Creates a single size instance if size does not already exist.
    """

    size_get_or_create(**payload.dict())
    return 201


class ProductOptionCreateInternalInput(Schema):
    status: int
    gross_price: float
    size_width: float | None = None
    size_height: float | None = None
    size_depth: float | None = None
    size_circumference: float | None = None
    variant_id: int | None = None

    # TODO: Validate that some parts of the size is present
    # TODO: Validate that either some size fields or variant is present


class ProductOptionCreateInternalOutput(Schema):
    id: int
    status: int
    gross_price: float
    size_id: int
    variant_id: int


def product_option_create_internal_api(
    request: HttpRequest, product_id: int, payload: ProductOptionCreateInternalInput
) -> tuple[int, ProductOptionCreateInternalOutput]:

    size = size_get_or_create(
        width=payload.size_width,
        height=payload.size_height,
        depth=payload.size_depth,
        circumference=payload.size_circumference,
    )

    product_option = product_option_create(
        product_id=product_id,
        gross_price=payload.gross_price,
        status=payload.status,
        size_id=size.id,
        variant_id=payload.variant_id,
    )

    return 201, ProductOptionCreateInternalOutput(
        id=product_option.id,
        status=product_option.status,
        gross_price=product_option.gross_price,
        size_id=product_option.size.id,
        variant_id=product_option.variant.id,
    )
