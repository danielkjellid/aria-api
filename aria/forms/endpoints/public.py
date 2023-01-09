import typing

from django.http import HttpRequest

from ninja import Router, Schema

from aria.forms.utils import (
    FormConfig,
    FormConfigBlockOverrides,
    FormConfigSection,
    FrontendFormElements,
    form_create_from_schema,
)
from aria.products.enums import ProductStatus

router = Router(tags=["Forms"])


class TestSchemaProp(Schema):
    other_property: str


class TestSchema(Schema):
    id: int
    property_1: str | None
    property_2: str
    property_3: int = 1
    property_4: list[int]
    # property_5: ProductStatus
    property_6: bool
    property_7: bool | None
    property_8: bool = True
    property_9: list[str]
    # property_10: FrontendFormElements


class FormOutput(Schema):
    key: str


@router.get("/", response={200: dict[str, typing.Any]})
def form_test_api(request: HttpRequest) -> FormOutput:
    # form1 = form_create_from_schema(schema=list[int])
    # form2 = form_create_from_schema(schema=list[TestSchema])
    print("-----------------")
    form3 = form_create_from_schema(
        schema=TestSchema,
        config=FormConfig(
            sections=[
                FormConfigSection(
                    name="Generelt", blocks=["property_1", "property_2", "property_3"]
                ),
                FormConfigSection(
                    name="Filer", blocks=["property_4", "property_5", "property_6"]
                ),
                FormConfigSection(
                    name="Resten", blocks=["property_4", "property_5", "property_6"]
                ),
            ],
            overrides=[
                FormConfigBlockOverrides(
                    id="property_1",
                    type="something",
                    element=FrontendFormElements.CHECKBOX,
                    placeholder="Test",
                ),
                FormConfigBlockOverrides(
                    id="property_99",
                    title="Yooo",
                    type="something",
                    element=FrontendFormElements.CHECKBOX,
                    placeholder="Test",
                ),
            ],
        ),
    )

    return 200, form3
