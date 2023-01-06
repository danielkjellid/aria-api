from django.http import HttpRequest

from ninja import File, Form, Router, Schema, UploadedFile

from aria.api.responses import codes_40x
from aria.api.schemas.responses import ExceptionResponse
from aria.api_auth.decorators import permission_required
from aria.product_attributes.selectors import (
    color_list,
    material_list,
    room_list,
    shape_list,
    variant_list,
)
from aria.product_attributes.services import variant_create

router = Router(tags=["Product attributes"])

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
    Endpoint for getting a list of all colors in the application.
    """

    colors = color_list()

    return [ColorListInternalOutput(**color.dict()) for color in colors]


###################################
# Material list internal endpoint #
###################################


class MaterialListInternalOutput(Schema):
    id: int
    name: str


@router.get(
    "materials/",
    response={
        200: list[MaterialListInternalOutput],
        codes_40x: ExceptionResponse,
    },
    summary="List all materials available.",
)
def material_list_internal_api(
    request: HttpRequest,
) -> list[MaterialListInternalOutput]:
    """
    Endpoint for getting a list of all materials in the application.
    """

    materials = material_list()

    return [MaterialListInternalOutput(**material.dict()) for material in materials]


###############################
# Room list internal endpoint #
###############################


class RoomListInternalOutput(Schema):
    id: int
    name: str


@router.get(
    "rooms/",
    response={
        200: list[RoomListInternalOutput],
        codes_40x: ExceptionResponse,
    },
    summary="List all rooms available.",
)
def room_list_internal_api(request: HttpRequest) -> list[RoomListInternalOutput]:
    """
    Endpoint for getting a list of all materials in the application.
    """

    rooms = room_list()

    return [RoomListInternalOutput(**room.dict()) for room in rooms]


################################
# Shape list internal endpoint #
################################


class ShapeListInternalOutput(Schema):
    id: int
    name: str
    image_url: str


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

    shape_records = shape_list()

    return [ShapeListInternalOutput(**shape.dict()) for shape in shape_records]


##################################
# Variant list internal endpoint #
##################################


class VariantListInternalOutput(Schema):
    id: int
    name: str
    is_standard: bool
    image_url: str | None
    thumbnail_url: str | None


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
    image_url: str | None
    thumbnail_url: str | None


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
