import decimal

from django.http import HttpRequest

import ninja
from ninja import Field, Router

from aria.api.fields import CustomField
from aria.files.types import UploadedFile, UploadedImageFile
from aria.forms.enums import FrontendFormElements
from aria.forms.schemas import FormOutput
from aria.forms.utils import form_create_from_schema
from aria.products.endpoints.internal import (
    ProductFileCreateInternalInput,
    ProductOptionCreateInBulkInternalInput,
)

router = Router(tags=["Forms"])


class ProductFileCreateFormOutput(ProductFileCreateInternalInput):
    file: UploadedFile


class Test(ninja.Schema):
    test: str | None = CustomField(
        "Test",
        alias="test_1",
        title="test",
        description="This is a test desc",
        min_length=4,
        repr="Test",
    )
    apply_filter: bool = False
    image: UploadedImageFile
    file: UploadedFile


@router.get("products/files/create/", response={200: FormOutput})
def form_product_file_create_internal_api(
    request: HttpRequest,
) -> tuple[int, FormOutput]:
    """
    Get the form for creating a product file instance.
    """

    form = form_create_from_schema(schema=Test)

    return 200, form


@router.get("products/options/bulk-create/", response={200: FormOutput})
def form_product_option_bulk_create_internal_api(
    request: HttpRequest,
) -> tuple[int, FormOutput]:

    form = form_create_from_schema(schema=list[ProductOptionCreateInBulkInternalInput])

    return 200, form


d = {
    "title": "ProductOptionCreateInBulkInternalInput",
    "type": "object",
    "properties": {
        "status": {
            "title": "Status",
            "default": 3,
            "allOf": [{"$ref": "#/definitions/ProductStatus"}],
        },
        "gross_price": {"title": "Pris", "type": "number"},
        "variant_id": {"title": "Variant", "type": "integer"},
        "size": {"$ref": "#/definitions/ProductOptionCreateInBulkSizeInternalInput"},
    },
    "required": ["gross_price"],
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
                "width": {"title": "Bredde i cm", "type": "number"},
                "height": {"title": "Høyde i cm", "type": "number"},
                "depth": {"title": "Dybde i cm", "type": "number"},
                "circumference": {
                    "title": "Omkrets i cm",
                    "description": "Omkrets kan brukes dersom alternativet har en sfærisk formn. Feltet kan ikke benyttes når de andre størrelsesfeltene er fylt ut.",
                    "type": "number",
                },
            },
        },
    },
}
