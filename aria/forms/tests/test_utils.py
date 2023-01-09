import typing
from dataclasses import dataclass

from ninja import Schema
from pydantic import BaseModel

from aria.forms.enums import FrontendFormElements
from aria.forms.records import (
    FormBlockEnumRecord,
    FormBlockRecord,
    FormRecord,
    FormSectionRecord,
)
from aria.forms.utils import form_create_from_schema
from aria.products.enums import ProductStatus


class MySchema(Schema):
    val_str: str
    val_bool: bool = False
    val_enum: ProductStatus = 1
    val_list_int: list[int]
    val_str_none: str | None


class MyModel(BaseModel):
    val: int


class TestFormsUtils:
    def test_util_form_create_from_schema(self):
        """
        Test that the form_create_from_schema util creates a form as expected.
        """

        form1 = form_create_from_schema(schema=MySchema, is_multipart_form=True)

        assert form1 == FormRecord(
            key="MySchema1",
            is_multipart_form=True,
            expects_list=False,
            required=["val_str", "val_list_int"],
            sections=[],
            blocks=[
                FormBlockRecord(
                    id="val_str",
                    title="Val Str",
                    type="string",
                    enum=None,
                    default_value=None,
                    element=FrontendFormElements.TEXT_INPUT,
                    placeholder=None,
                    help_text=None,
                    display_word_count=False,
                    hidden_label=False,
                    col_span=None,
                ),
                FormBlockRecord(
                    id="val_bool",
                    title="Val Bool",
                    type="boolean",
                    enum=None,
                    default_value=0,
                    element=FrontendFormElements.CHECKBOX,
                    placeholder=None,
                    help_text=None,
                    display_word_count=False,
                    hidden_label=False,
                    col_span=None,
                ),
                FormBlockRecord(
                    id="val_enum",
                    title="ProductStatus",
                    type="integer",
                    enum=[
                        FormBlockEnumRecord(name="Draft", value=1),
                        FormBlockEnumRecord(name="Hidden", value=2),
                        FormBlockEnumRecord(name="Available", value=3),
                        FormBlockEnumRecord(name="Discontinued", value=4),
                    ],
                    default_value=1,
                    element=FrontendFormElements.SELECT,
                    placeholder=None,
                    help_text=None,
                    display_word_count=False,
                    hidden_label=False,
                    col_span=None,
                ),
                FormBlockRecord(
                    id="val_list_int",
                    title="Val List Int",
                    type="array",
                    enum=None,
                    default_value=None,
                    element=FrontendFormElements.MULTISELECT,
                    placeholder=None,
                    help_text=None,
                    display_word_count=False,
                    hidden_label=False,
                    col_span=None,
                ),
                FormBlockRecord(
                    id="val_str_none",
                    title="Val Str None",
                    type="string",
                    enum=None,
                    default_value=None,
                    element=FrontendFormElements.TEXT_INPUT,
                    placeholder=None,
                    help_text=None,
                    display_word_count=False,
                    hidden_label=False,
                    col_span=None,
                ),
            ],
        )

        assert "val_str_none" not in form1.required

        form2 = form_create_from_schema(schema=list[MySchema])
        assert form2.expects_list is True
        # Blocks should be the same.
        assert form2.blocks == form1.blocks

        sections = [
            FormSectionRecord(
                name="Section 1", blocks=["val_str", "val_bool", "val_enum"]
            ),
            FormSectionRecord(
                name="Section 2", blocks=["val_list_int", "val_str_none"]
            ),
        ]

        form3 = form_create_from_schema(
            schema=MySchema,
            sections=sections,
        )

        assert form3.sections == sections
        # Blocks should be the same.
        assert form3.blocks == form1.blocks

        form4 = form_create_from_schema(
            schema=MySchema,
            overrides=[
                FormBlockRecord(
                    id="val_str",
                    title="Overridden",
                    type="overridden",
                    default_value=1,
                )
            ],
        )

        assert form4.blocks[0].title == "Overridden"
        assert form4.blocks[0].type == "overridden"
        assert form4.blocks[0].default_value == 1
        # All remaining blocks should be unchanged, and the same as in form1.
        assert form4.blocks[1:] == form1.blocks[1:]
