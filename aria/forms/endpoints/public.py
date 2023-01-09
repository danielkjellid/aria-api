import typing

from django.http import HttpRequest

from ninja import Router, Schema

from aria.forms.schemas import FormOutput
from aria.forms.utils import form_create_from_schema
from aria.products.enums import ProductStatus

router = Router(tags=["Forms"])


class TestSchema(Schema):
    id: int
    property_1: str | None
    property_2: str
    property_3: int = 1
    property_4: list[int]
    property_5: ProductStatus = ProductStatus.AVAILABLE
    property_6: bool
    property_7: bool | None
    property_8: bool = True
    property_9: list[str]


@router.get("/", response={200: FormOutput})
def form_test_api(request: HttpRequest) -> FormOutput:
    # form1 = form_create_from_schema(schema=list[int])
    # form2 = form_create_from_schema(schema=list[TestSchema])
    print("-----------------")
    form3 = form_create_from_schema(schema=TestSchema)

    return 200, form3
