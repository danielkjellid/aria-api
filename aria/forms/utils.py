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


class FormConfigBlockOverrides(pydantic.BaseModel):
    id: str
    title: str | None
    type: str | None
    enum: typing.Any | None
    default: str | int | bool | None
    element: FrontendFormElements | None
    placeholder: str | None


class FormConfig(pydantic.BaseModel):
    is_multipart_form: bool = False
    sections: list[FormConfigSection] | None
    overrides: list[FormConfigBlockOverrides] | None


DEFAULT_ELEMENT_MAPPING: typing.Final[dict[str, str]] = {
    "string": FrontendFormElements.TEXT_INPUT,
    "integer": FrontendFormElements.NUMBER_INPUT,
    "boolean": FrontendFormElements.CHECKBOX,
    "enum": FrontendFormElements.SELECT,
    "array": FrontendFormElements.MULTISELECT,
}


class FormBlockEnum(pydantic.BaseModel):
    name: str
    value: typing.Any


class FormBlock(pydantic.BaseModel):
    id: str
    title: str
    type: str
    enum: list[FormBlockEnum] | None
    default: int | str | bool | None
    element: FrontendFormElements
    placeholder: str | None


class FormSection(pydantic.BaseModel):
    name: str
    blocks: list[str]


class Form(pydantic.BaseModel):
    key: str
    is_multipart_form: bool = False
    expects_list: bool = False
    required: list[str]
    sections: list[FormSection]
    blocks: list[FormBlock]


def _validate_schema(schema: Schema) -> tuple[type | None, bool]:
    if _is_list(type_annotation=schema):
        inner_type, is_list = _get_inner_list_type(type_annotation=schema)

        if _is_pydantic_model(type_annotation=inner_type):
            schema_from_type = inner_type
            return schema_from_type, is_list

    elif _is_pydantic_model(type_annotation=schema):
        schema_from_type = schema
        return schema_from_type, False

    else:
        logger.info(
            "Could not generate form from passed schema. Schema is not a pydantic "
            "subclass nor a list of pydantic subclasses.",
            schema=schema,
            is_list=False,
        )
        return None, False


def _format_enum_from_type(typ: type) -> list[FormBlockEnum]:
    # If passed enum is a django choices field, we can take advantaged
    # of the defined label.
    if issubclass(typ, IntegerChoices | TextChoices):
        formatted_label_values = [
            FormBlockEnum(name=item.label, value=item.value) for item in typ
        ]
    elif issubclass(typ, Enum):
        formatted_label_values = [
            FormBlockEnum(name=item.name.replace("_", " ").title(), value=item.value)
            for item in typ
        ]
    else:
        formatted_label_values = [FormBlockEnum(name=item, value=item) for item in typ]

    return formatted_label_values


def form_create_from_schema(
    *, schema: Schema, config: FormConfig | None = None
) -> Form | None:
    schema_type, schema_is_list = _validate_schema(schema=schema)

    if schema_type is None:
        return

    schema_definition = schema_type.schema()
    blocks = []
    definitions = schema_definition.get("definitions", None)

    for key, value in schema_definition["properties"].items():
        title: str = value.get("title", None)
        typ: str = value.get("type", None)
        enum: list[FormBlockEnum] | None = None
        default: str | int | bool | None = value.get("default", None)
        placeholder: str | None = None

        value_ref = value.get("$ref", None)

        if value_ref and definitions:
            # Get the typename from the reference and find it in the definitions' dict.
            ref = value_ref.rsplit("/", 1)[-1]
            definition = definitions.get(ref)

            # Replace values with values in the definition.
            title = definition.get("title", None)
            typ = definition.get("type", "enum")
            enum_from_definition = definition.get("enum", None)

            if enum_from_definition:
                field_type = schema_type.__fields__[key].type_
                enum = _format_enum_from_type(typ=field_type)

        if enum:
            element = DEFAULT_ELEMENT_MAPPING["enum"]
        else:
            element = DEFAULT_ELEMENT_MAPPING[typ]

        overrides = {}
        override_config = next(
            (override for override in config.overrides if override.id == key),
            None,
        )

        if override_config:
            overrides = override_config.dict(
                exclude_unset=True, exclude_defaults=True, exclude_none=True
            )

        block = FormBlock(
            id=key,
            title=overrides.get("title", title),
            type=overrides.get("type", typ),
            enum=overrides.get("enum", enum),
            default=overrides.get("default", default),
            element=overrides.get("element", element),
            placeholder=overrides.get("placeholder", placeholder),
        )

        blocks.append(block)

    if config.overrides:
        # Since we also want to be able to configure fields that does not
        # necessarily exist on the schema, we allow field overrides not matching
        # any id's to be added as their own individual field. A good example of
        # this is how multipart/form is defined in Django ninja, where the blob
        # is passed directly in the request, and not in the schema payload.
        overrides_non_existent_block = [
            FormBlock(**override.dict())
            for override in config.overrides
            if override.id not in [block.id for block in blocks]
        ]

        blocks.extend(overrides_non_existent_block)

    return Form(
        key=schema_definition["title"],
        expects_list=schema_is_list,
        required=schema_definition["required"],
        sections=[
            FormSection(name=section.name, blocks=section.blocks)
            for section in config.sections
        ],
        blocks=blocks,
    )
