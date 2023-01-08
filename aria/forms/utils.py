import typing
from enum import Enum

from django.db.models import IntegerChoices, TextChoices

import pydantic
import structlog
from ninja import Schema

logger = structlog.get_logger(__name__)


class TestSchemaProp(Schema):
    property_3: str


class TestSchema(Schema):
    id: int
    property_1: str | None
    property_2: str
    property_3: TestSchemaProp
    property_4: list[TestSchemaProp]
    property_5: TestSchemaProp | None = None
    property_6: bool
    property_7: bool | None
    property_8: bool = True


d = {
    "title": "TestSchema",
    "type": "object",
    "properties": {
        "id": {"title": "Id", "type": "integer"},
        "property_1": {"title": "Property 1", "type": "string"},
        "property_2": {"title": "Property 2", "type": "string"},
        "property_3": {"title": "Property 3", "default": 1, "type": "integer"},
        "property_4": {
            "title": "Property 4",
            "type": "array",
            "items": {"type": "integer"},
        },
        "property_5": {"$ref": "#/definitions/ProductStatus"},
        "property_6": {"title": "Property 6", "type": "boolean"},
        "property_7": {"title": "Property 7", "type": "boolean"},
        "property_8": {"title": "Property 8", "default": True, "type": "boolean"},
    },
    "required": ["id", "property_2", "property_4", "property_5", "property_6"],
    "definitions": {
        "ProductStatus": {
            "title": "ProductStatus",
            "description": "An enumeration.",
            "enum": [1, 2, 3, 4],
            "type": "integer",
        }
    },
}


def _is_list(*, type_annotation: type) -> bool:
    return typing.get_origin(type_annotation) is list


def _is_pydantic_model(*, type_annotation: type) -> bool:
    return issubclass(type_annotation, pydantic.BaseModel) or (
        hasattr(type_annotation, "__pydantic_model__")
        and issubclass(type_annotation.__pydantic_model__, pydantic.BaseModel)
    )


def _get_inner_list_type(type_annotation: type) -> tuple[type, bool]:
    is_list = _is_list(type_annotation=type_annotation)
    if is_list:
        type_annotation = _unwrap_item_type_from_list(type_annotation=type_annotation)
    return type_annotation, is_list


def _unwrap_item_type_from_list(*, type_annotation: type) -> type:
    return typing.get_args(type_annotation)[0]


class FrontendFormElements(Enum):
    TEXT_INPUT = "textInput"
    NUMBER_INPUT = "numberInput"
    CHECKBOX = "checkbox"
    SELECT = "select"
    MULTISELECT = "multiselect"
    LIST_BOX_FILTER = "listBoxFilter"
    LIST_BOX_FILTER_NUMBER = "listBoxFilterNumber"
    EDITOR = "editor"
    ACTION = "action"
    IMAGE = "image"
    FILE = "file"


class FormConfigSection(pydantic.BaseModel):
    name: str
    blocks: list[str]


class FormConfigOverridesAttrs(pydantic.BaseModel):
    element: FrontendFormElements | None
    placeholder: str | None


class FormConfigOverrides(pydantic.BaseModel):
    identifier: str
    title: str | None
    type: str | None
    enum: typing.Any | None
    attrs: FormConfigOverridesAttrs | None


class FormConfig(pydantic.BaseModel):
    sections: list[FormConfigSection] | None
    overrides: list[FormConfigOverrides] | None


DEFAULT_ELEMENT_MAPPING: typing.Final[dict[str, str]] = {
    "string": FrontendFormElements.TEXT_INPUT,
    "integer": FrontendFormElements.NUMBER_INPUT,
    "boolean": FrontendFormElements.CHECKBOX,
    "enum": FrontendFormElements.SELECT,
    "array": FrontendFormElements.MULTISELECT,
}


class Form(pydantic.BaseModel):
    key: str
    expects_list: bool = False
    required: list[str]
    sections: list[FormConfigSection]
    blocks: dict[str, typing.Any]


def form_create_from_schema(
    *, schema: Schema, config: FormConfig | None = None
) -> dict[str, typing.Any] | None:
    form = {}
    schema_is_list = False

    if _is_list(type_annotation=schema):
        inner_type, is_list = _get_inner_list_type(type_annotation=schema)

        if _is_pydantic_model(type_annotation=inner_type):
            schema_from_type = inner_type
            schema_is_list = is_list
        else:
            logger.info(
                "Could not generate form from passed schema. "
                "Schema is not a pydantic subclass.",
                schema=inner_type,
                is_list=is_list,
            )
            return

    elif _is_pydantic_model(type_annotation=schema):
        schema_from_type = schema

    else:
        logger.info(
            "Could not generate form from passed schema. Schema is not a pydantic "
            "subclass nor a list of pydantic subclasses.",
            schema=schema,
            is_list=False,
        )
        return

    # print(schema.schema())

    schema_definition = schema_from_type.schema()
    form["key"] = schema_definition["title"]
    form["expects_list"] = schema_is_list
    form["required"] = schema_definition["required"]
    form["sections"] = []
    form["blocks"] = {}

    definitions = schema_definition.get("definitions", None)

    for key, value in schema_definition["properties"].items():
        block = {"title": "", "type": ""}
        block_attrs = {}

        value_ref = value.get("$ref", None)

        if value_ref and definitions:
            # Get the typename from the reference and find it in the definitions dict.
            ref = value_ref.rsplit("/", 1)[-1]
            definition = definitions.get(ref)

            # Flatten object and populate needed values.
            title = definition.get("title", None)

            if title:
                block["title"] = title

            typ = definition.get("type", None)

            if typ:
                block["type"] = typ

            # Optional values
            enum = definition.get("enum", None)

            if enum:
                field_type = schema_from_type.__fields__[key].type_
                print(field_type.__class__.__name__)
                # If passed enum is a django choices field, we can take advantaged
                # of the defined label.

                print(issubclass(field_type, Enum))

                if issubclass(field_type, IntegerChoices | TextChoices):
                    mapped_enum_label_values = [
                        {"name": item.label, "value": item.value} for item in field_type
                    ]
                elif issubclass(field_type, Enum):
                    mapped_enum_label_values = [
                        {
                            "name": item.name.replace("_", " ").title(),
                            "value": item.value,
                        }
                        for item in field_type
                    ]
                else:
                    mapped_enum_label_values = [
                        {"name": item, "value": item} for item in field_type
                    ]

                block["enum"] = mapped_enum_label_values
        else:
            block["title"] = value["title"]
            block["type"] = value["type"]

        default = value.get("default", None)
        is_enum = block.get("enum", False)

        if is_enum:
            block_attrs["element"] = DEFAULT_ELEMENT_MAPPING["enum"]
        else:
            block_attrs["element"] = DEFAULT_ELEMENT_MAPPING[block["type"]]

        if default is not None:
            block["default"] = default

        block["attrs"] = block_attrs
        form_block = {key: block}

        form["blocks"].update(form_block)

    if config is not None:
        if config.sections:
            form["sections"] = [section.dict() for section in config.sections]
        if config.overrides:
            for override in config.overrides:
                form_block = form["blocks"].get(override.identifier, None)
                if form_block is None:
                    logger.warning(
                        "Not able to complete override, not element with identifier in blocks.",
                        identifier=override.identifier,
                    )
                override_dict = override.dict()
                override_dict.pop("identifier")

                for key, value in override_dict.items():
                    if value:
                        form_block[key] = value

    # print(form)
    return form


x = {
    "key": "TestSchema",
    "expects_list": False,
    "required": ["id", "property_2", "property_4", "property_5", "property_6"],
    "blocks": {
        "id": {"title": "Id", "type": "integer"},
        "property_1": {"title": "Property 1", "type": "string"},
        "property_2": {"title": "Property 2", "type": "string"},
        "property_3": {"title": "Property 3", "type": "integer"},
        "property_4": {"title": "Property 4", "type": "array"},
        "property_5": {
            "title": "ProductStatus",
            "type": "integer",
            "enum": [1, 2, 3, 4],
        },
        "property_6": {"title": "Property 6", "type": "boolean"},
        "property_7": {"title": "Property 7", "type": "boolean"},
        "property_8": {"title": "Property 8", "type": "boolean"},
    },
}
