from django.http import HttpRequest

from ninja import Router, UploadedFile

from aria.forms.schemas import FormOutput
from aria.forms.utils import form_create_from_schema
from aria.products.endpoints.internal import (
    ProductFileCreateInternalInput,
    ProductOptionCreateInBulkInternalInput,
)

router = Router(tags=["Forms"])


class ProductFileCreateFormOutput(ProductFileCreateInternalInput):
    file: UploadedFile


@router.get("products/files/create/", response={200: FormOutput})
def form_product_file_create_internal_api(
    request: HttpRequest,
) -> tuple[int, FormOutput]:
    """
    Get the form for creating a product file instance.
    """

    form = form_create_from_schema(schema=ProductFileCreateFormOutput)

    return 200, form


@router.get("products/options/bulk-create/", response={200: FormOutput})
def form_product_option_bulk_create_internal_api(
    request: HttpRequest,
) -> tuple[int, FormOutput]:

    form = form_create_from_schema(schema=ProductOptionCreateInBulkInternalInput)

    return 200, form


d = {
    "title": "ProductOptionCreateInBulkInternalInput",
    "type": "object",
    "properties": {
        "status": {"$ref": "#/definitions/ProductStatus"},
        "gross_price": {"title": "Gross Price", "type": "number"},
        "variant_id": {"title": "Variant Id", "type": "integer"},
        "size": {"$ref": "#/definitions/ProductOptionCreateInBulkSizeInternalInput"},
    },
    "required": ["status", "gross_price"],
    "definitions": {
        "ProductStatus": {
            "title": "ProductStatus",
            "description": "An enumeration.",
            "enum": [1, 2, 3, 4],
            "type": "integer",
        },
        "ProductOptionCreateInBulkSizeInternalInput": {
            "title": "ProductOptionCreateInBulkSizeInternalInput",
            "type": "object",
            "properties": {
                "width": {"title": "Width", "type": "number"},
                "height": {"title": "Height", "type": "number"},
                "depth": {"title": "Depth", "type": "number"},
                "circumference": {"title": "Circumference", "type": "number"},
            },
        },
    },
}
