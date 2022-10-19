from django.http import HttpRequest
from django.shortcuts import get_object_or_404

from ninja import File, Form, Query, Router, Schema, UploadedFile

from aria.api.decorators import paginate
from aria.api.responses import codes_40x
from aria.api.schemas.responses import ExceptionResponse
from aria.api_auth.decorators import permission_required
from aria.products.enums import ProductStatus, ProductUnit
from aria.products.models import Product, Size, Variant
from aria.products.schemas.filters import ProductListFilters
from aria.products.selectors.colors import color_list
from aria.products.selectors.core import product_list
from aria.products.selectors.shapes import shape_list
from aria.products.selectors.variants import variant_list
from aria.products.services.product_files import product_file_create
from aria.products.services.product_images import product_image_create
from aria.products.services.product_options import (
    product_option_create,
    product_options_bulk_create_options_and_sizes,
)
from aria.products.services.sizes import size_get_or_create
from aria.products.services.variants import variant_create

router = Router(tags=["Products"])


##################################
# Product list internal endpoint #
##################################


class ProductListInternalOutputSupplier(Schema):
    name: str
    origin_country: str
    origin_country_flag: str


class ProductListInternalOutput(Schema):
    id: int
    name: str
    slug: str
    status: str
    supplier: ProductListInternalOutputSupplier
    unit: str


@router.get(
    "/",
    response={
        200: list[ProductListInternalOutput],
        codes_40x: ExceptionResponse,
    },
    summary="List all products",
    url_name="internal-products-index",  # Temporary.
)
@permission_required(
    ["products.product.view", "products.product.management", "products.product.admin"],
)
@paginate(page_size=50)
def product_list_internal_api(
    request: HttpRequest, filters: ProductListFilters = Query(...)
) -> list[ProductListInternalOutput]:
    """
    Retrieve a list of all products in the application.
    """

    products = product_list(filters=filters.dict())
    return [ProductListInternalOutput(**product.dict()) for product in products]


####################################
# Product create internal endpoint #
####################################


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
    absorption: float | None = None
    display_price: bool
    can_be_purchased_online: bool
    can_be_picked_up: bool

    # Relationships - should already exist.
    supplier_id: int
    category_ids: list[int]
    shape_ids: list[int]
    color_ids: list[int]


@router.post(
    "create/",
    response={
        200: ProductCreateInternalInput,
        codes_40x: ExceptionResponse,
    },
    summary="Create a single product instance.",
)
def product_create_internal_api(
    request: HttpRequest,
) -> tuple[int, ProductCreateInternalInput]:
    """
    Create a single product instance.
    """


##########################################
# Product image create internal endpoint #
##########################################


class ProductImageCreateInternalInput(Schema):
    apply_filter: bool = False


class ProductImageCreateInternalOutput(Schema):
    id: int
    product_id: int
    image_url: str | None


@router.post(
    "{product_id}/images/create/",
    response={
        201: ProductImageCreateInternalOutput,
        codes_40x: ExceptionResponse,
    },
    summary="Create an image associated to a product.",
)
@permission_required(["products.product.management", "products.product.admin"])
def product_image_create_internal_api(
    request: HttpRequest,
    product_id: int,
    payload: ProductImageCreateInternalInput = Form(...),
    file: UploadedFile = File(...),
) -> tuple[int, ProductImageCreateInternalOutput]:
    """
    Create an image associated to a certain product based on a product's id.
    """

    product = get_object_or_404(Product, pk=product_id)
    product_image = product_image_create(
        product=product, image=file, apply_filter=payload.apply_filter
    )

    return 201, ProductImageCreateInternalOutput(**product_image.dict())


#########################################
# Product file create internal endpoint #
#########################################


class ProductFileCreateInternalInput(Schema):
    name: str


class ProductFileCreateInternalOutput(Schema):
    id: int
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
@permission_required(["products.product.management", "products.product.admin"])
def product_file_create_internal_api(
    request: HttpRequest,
    product_id: int,
    payload: ProductFileCreateInternalInput = Form(...),
    file: UploadedFile = File(...),
) -> tuple[int, ProductFileCreateInternalOutput]:
    """
    Create a file associated to a certain product based on a product's id.
    """

    product = get_object_or_404(Product, pk=product_id)
    product_file = product_file_create(product=product, name=payload.name, file=file)

    return 201, ProductFileCreateInternalOutput(**product_file.dict())


##################################
# Variant list internal endpoint #
##################################


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
@permission_required(["products.product.management", "products.product.admin"])
def variant_list_internal_api(request: HttpRequest) -> list[VariantListInternalOutput]:
    """
    Get a list of all variants in the application.
    """

    variants = variant_list()

    return [VariantListInternalOutput(**variant.dict()) for variant in variants]


####################################
# Variant create internal endpoint #
####################################


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
@permission_required(["products.product.management", "products.product.admin"])
def variant_create_internal_api(
    request: HttpRequest,
    payload: VariantCreateInternalInput = Form(...),
    file: UploadedFile = File(...),
) -> tuple[int, VariantCreateInternalOutput]:
    """
    Creates a single variant instance.
    """

    variant_record = variant_create(
        name=payload.name, is_standard=payload.is_standard, thumbnail=file
    )

    return 201, VariantCreateInternalOutput(**variant_record.dict())


###########################################
# Product option create internal endpoint #
###########################################


class ProductOptionCreateInternalSizeInput(Schema):
    width: float | None = None
    height: float | None = None
    depth: float | None = None
    circumference: float | None = None


class ProductOptionCreateInternalInput(Schema):
    status: ProductStatus
    gross_price: float
    variant_id: int | None = None
    size: ProductOptionCreateInternalSizeInput | None = None


class ProductOptionCreateInternalOutput(Schema):
    id: int
    status: ProductStatus
    gross_price: float
    size_id: int | None
    variant_id: int | None


@router.post(
    "{product_id}/options/create/",
    response={
        201: ProductOptionCreateInternalOutput,
        codes_40x: ExceptionResponse,
    },
    summary="Create a new product option.",
)
@permission_required("products.product.management")
def product_option_create_internal_api(
    request: HttpRequest, product_id: int, payload: ProductOptionCreateInternalInput
) -> tuple[int, ProductOptionCreateInternalOutput]:
    """
    Create a single product option instance belonging to a product based in id.
    """
    size = None
    size_record = None
    variant = None

    product = get_object_or_404(Product, pk=product_id)

    if payload.size is not None:
        size_record = size_get_or_create(
            width=payload.size.width if payload.size else None,
            height=payload.size.height if payload.size else None,
            depth=payload.size.depth if payload.size else None,
            circumference=payload.size.circumference if payload.size else None,
        )

    if size_record:
        size = get_object_or_404(Size, pk=size_record.id)

    if payload.variant_id:
        variant = get_object_or_404(Variant, pk=payload.variant_id)

    product_option_record = product_option_create(
        product=product,
        gross_price=payload.gross_price,
        status=payload.status,
        size=size,
        variant=variant,
    )

    return 201, ProductOptionCreateInternalOutput(**product_option_record.dict())


################################################
# Product option bulk create internal endpoint #
################################################


class ProductOptionCreateInBulkInternalSizeInput(Schema):
    width: float | None = None
    height: float | None = None
    depth: float | None = None
    circumference: float | None = None


class ProductOptionCreateInBulkInternalInput(Schema):
    status: ProductStatus
    gross_price: float
    variant_id: int | None = None
    size: ProductOptionCreateInBulkInternalSizeInput | None = None


class ProductOptionCreateInBulkInternalOutput(Schema):
    id: int
    status: ProductStatus
    gross_price: float
    size_id: int | None
    variant_id: int | None


@router.post(
    "{product_id}/options/bulk-create/",
    response={
        200: list[ProductOptionCreateInBulkInternalOutput],
        codes_40x: ExceptionResponse,
    },
    summary="Create new product options in bulk.",
)
@permission_required(["products.product.management", "products.product.admin"])
def product_option_bulk_create_internal_api(
    request: HttpRequest,
    product_id: int,
    payload: list[ProductOptionCreateInBulkInternalInput],
) -> list[ProductOptionCreateInBulkInternalOutput]:
    """
    Create multiple product options in bulk belonging to a single product instance based
    on id.
    """

    product = get_object_or_404(Product, pk=product_id)
    options = product_options_bulk_create_options_and_sizes(
        product=product, options=payload  # type: ignore
    )

    return [
        ProductOptionCreateInBulkInternalOutput(**option.dict()) for option in options
    ]


################################
# Color list internal endpoint #
################################


class ColorListInternalOutput(Schema):
    id: int
    name: str
    color_hex: str


@router.get(
    "colors/",
    response={
        200: list[ColorListInternalOutput],
        codes_40x: ExceptionResponse,
    },
    summary="List all colors available.",
)
def color_list_internal_api(
    request: HttpRequest,
) -> list[ColorListInternalOutput]:
    """
    Endpoint for getting a list of all sizes in the application.
    """

    colors = color_list()

    return [ColorListInternalOutput(**color.dict()) for color in colors]


################################
# Shape list internal endpoint #
################################


class ShapeListInternalOutput(Schema):
    id: int
    name: str
    image: str


@router.get(
    "shapes/",
    response={
        200: list[ShapeListInternalOutput],
        codes_40x: ExceptionResponse,
    },
    summary="List all shapes available.",
)
def shape_list_internal_api(request: HttpRequest) -> list[ShapeListInternalOutput]:
    """
    Endpoint for getting a list of all shapes in the application.
    """

    shapes = shape_list()

    return [ShapeListInternalOutput(**shape.dict()) for shape in shapes]
