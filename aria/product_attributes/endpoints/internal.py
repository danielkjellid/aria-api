from django.http import HttpRequest

from ninja import Router, Schema

from aria.api.responses import codes_40x
from aria.api.schemas.responses import ExceptionResponse
from aria.product_attributes.selectors import shape_list

router = Router(tags=["Product attributes"])


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

    shape_records = shape_list()

    return [ShapeListInternalOutput(**shape.dict()) for shape in shape_records]
