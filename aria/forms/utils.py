from enum import Enum

from django.db.models import IntegerChoices, TextChoices

import structlog
from ninja import Schema

from aria.forms.constants import FORM_ELEMENT_MAPPING
from aria.forms.helpers import get_inner_list_type, is_list, is_pydantic_model
from aria.forms.records import (
    FormBlockEnumRecord,
    FormBlockRecord,
    FormRecord,
    FormSectionRecord,
)

logger = structlog.get_logger(__name__)


def _validate_schema(schema: Schema) -> tuple[type | None, bool]:
    if is_list(type_annotation=schema):
        inner_type, is_lst = get_inner_list_type(type_annotation=schema)

        if is_pydantic_model(type_annotation=inner_type):
            schema_from_type = inner_type
            return schema_from_type, is_lst

    elif is_pydantic_model(type_annotation=schema):
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


def _format_enum_from_type(typ: type) -> list[FormBlockEnumRecord]:
    # If passed enum is a django choices field, we can take advantaged
    # of the defined label.
    if issubclass(typ, IntegerChoices | TextChoices):
        formatted_label_values = [
            FormBlockEnumRecord(name=item.label, value=item.value) for item in typ
        ]
    elif issubclass(typ, Enum):
        formatted_label_values = [
            FormBlockEnumRecord(
                name=item.name.replace("_", " ").title(), value=item.value
            )
            for item in typ
        ]
    else:
        formatted_label_values = [
            FormBlockEnumRecord(name=item, value=item) for item in typ
        ]

    return formatted_label_values


def form_create_from_schema(
    *,
    schema: Schema,
    is_multipart_form: bool = False,
    overrides: list[FormBlockRecord] | None = None,
    sections: list[FormSectionRecord] | None = None,
) -> FormRecord | None:

    overrides = overrides if overrides is not None else []
    sections = sections if sections is not None else []

    schema_type, schema_is_list = _validate_schema(schema=schema)

    if schema_type is None:
        return

    schema_definition = schema_type.schema()
    blocks = []
    definitions = schema_definition.get("definitions", None)

    for key, value in schema_definition["properties"].items():
        title: str = value.get("title", None)
        typ: str = value.get("type", None)
        enum: list[FormBlockEnumRecord] | None = None
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

        # Even though type of enum value is something else, we want to default enums
        # to use select HTML elements.
        if enum:
            element = FORM_ELEMENT_MAPPING["enum"]
        else:
            element = FORM_ELEMENT_MAPPING[typ]

        overrides_dict = {}
        override_config = next(
            (override for override in overrides if override.id == key),
            None,
        )

        if override_config:
            overrides_dict = override_config.dict(
                exclude_unset=True, exclude_defaults=True, exclude_none=True
            )

        block = FormBlockRecord(
            id=key,
            title=overrides_dict.get("title", title),
            type=overrides_dict.get("type", typ),
            enum=overrides_dict.get("enum", enum),
            default=overrides_dict.get("default", default),
            element=overrides_dict.get("element", element),
            placeholder=overrides_dict.get("placeholder", placeholder),
        )

        blocks.append(block)

    if overrides:
        # Since we also want to be able to configure fields that does not
        # necessarily exist on the schema, we allow field overrides not matching
        # any id's to be added as their own individual field. A good example of
        # this is how multipart/form is defined in Django ninja, where the blob
        # is passed directly in the request, and not in the schema payload.
        overrides_non_existent_block = [
            FormBlockRecord(**override.dict())
            for override in overrides
            if override.id not in [block.id for block in blocks]
        ]

        blocks.extend(overrides_non_existent_block)

    return FormRecord(
        key=schema_definition["title"],
        is_multipart_form=is_multipart_form,
        expects_list=schema_is_list,
        required=schema_definition["required"],
        sections=[
            FormSectionRecord(name=section.name, blocks=section.blocks)
            for section in sections
        ],
        blocks=blocks,
    )
