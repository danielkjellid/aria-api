from __future__ import annotations

from enum import Enum
from typing import Any, TypedDict, TypeVar

from django.db.models import IntegerChoices, TextChoices

import structlog
from ninja import Schema

from aria.core.humps import camelize
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
    """
    Validate that passed schema is either a subclassed pydantic model, or a list of
    subclassed pydantic models.
    """
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
        return None, is_list(schema)


def _format_enum_from_type(typ: type) -> list[FormBlockEnumRecord]:
    """
    Format schema field's enum type into a key - value format, taking advantage
    of Django's human-readable labels where applicable.
    """

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


class JSONSchemaProperties(TypedDict, total=False):
    """
    The property dict only generates values that are populated, so None values will
    not be a part of the returned schema.
    """

    title: str
    type: str
    default: Any
    format: str  # Indicates if the type has a special format, for instance 'binary'.
    description: str
    enum: list[Any]
    allOf: list[dict[str, str]]
    alias: str  # The public name of the field,
    const: Any  # Field is required and *must* take its default value

    # Ints:
    maximum: int  # Requires field to be "less than or equal to" (le param).
    minimum: int  # Requires field to be "greater than or equal to" (ge param).
    exclusiveMinimum: int  # Requires the field to be "greater than" (gt param).
    exclusiveMaximum: int  # Requires the field to be "less than" (lt param).
    multipleOf: float  # Requires the field to be "a multiple of" (modulus).

    # Lists:
    minItems: int  # Requires field (list) to have a minimum number of elements.
    maxItems: int  # Requires field (list) to have a maximum number of elements.
    uniqueItems: bool  # Requires field (list) not to have duplicated elements.

    # Strings:
    minLength: int  # Requires field (str) to have a minimum length.
    maxLength: int  # Requires field (str) to have a maximum length.
    pattern: str  # Requires field (str) match against a regex pattern string.

    # Custom:
    placeholder: str
    help_text: str
    display_word_count: bool
    hidden_label: bool
    col_span: int
    allow_set_primary_image: bool
    allow_set_filter_image: bool


class JSONSchema(TypedDict):
    title: str
    description: str
    type: str
    required: list[str]
    properties: dict[str, JSONSchemaProperties | str]
    definitions: dict[str, JSONSchema | JSONSchemaProperties]


T_JSON_SCHEMA_PROPERTIES = TypeVar(
    "T_JSON_SCHEMA_PROPERTIES", bound=dict[str, str | JSONSchemaProperties]
)
T_JSON_SCHEMA_DEFINITIONS = TypeVar(
    "T_JSON_SCHEMA_DEFINITIONS", bound=dict[str, JSONSchema | JSONSchemaProperties]
)


# The supported property keys should match the fields defined in FormBlockRecord.
SUPPORTED_PROPERTY_KEYS = [
    "title",
    "type",
    "default_value",
    "description",
    "enum",
    "placeholder",
    "help_text",
    "display_word_count",
    "hidden_label",
    "col_span",
    "allow_set_primary_image",
    "allow_set_filter_image",
]
# If no mapping is provided, we'll fall back to use the key in supported keys.
PROPERTY_KEYS_SCHEMA_MAPPING = {
    "default_value": "default",
    "enum": "enum",
    "all_of": "allOf",
    "exclusive_maximum": "exclusiveMaximum",
    "exclusive_minimum": "exclusiveMinimum",
    "multiple_of": "multipleOf",
    "min_items": "minItems",
    "max_items": "maxItems",
    "unique_items": "uniqueItems",
    "min_length": "minLength",
    "max_length": "maxLength",
}


def _extract_property_values(value: Any) -> dict[str, Any]:
    property_values = {}

    for key in SUPPORTED_PROPERTY_KEYS:
        mapped_key = PROPERTY_KEYS_SCHEMA_MAPPING.get(key, None)
        key_to_get = mapped_key if mapped_key else key
        value_to_append = value.get(key_to_get, None)

        if value_to_append is None:
            continue

        property_values[key] = value_to_append
    return property_values


class SkipParentFormBlockCreationException(Exception):
    pass


def _build_form_blocks(
    schema_type_annotation: Schema,
    schema_properties: T_JSON_SCHEMA_PROPERTIES,
    schema_definitions: T_JSON_SCHEMA_DEFINITIONS | None,
    parent: str | None = None,
) -> list[FormBlockRecord]:
    """
    Build form blocks based on provided schema properties.
    """

    form_blocks = []
    definitions = schema_definitions if schema_definitions else {}

    for key, value in schema_properties.items():
        camelized_key = camelize(key)
        property_values = _extract_property_values(value)
        property_all_of_list = value.get("allOf", [])
        property_value_ref = value.get("$ref", None)

        if parent:
            property_values["parent"] = parent

        # If we find any reference values we want to add them to a list to later
        # iterate over them and add their definitions as form blocks.
        if property_value_ref:
            property_all_of_list.append(value)

        if property_all_of_list and definitions:
            try:
                for reference in property_all_of_list:
                    # Get the typename from the reference and find it in the
                    # definitions' dict.
                    definition_key = reference.get("$ref", "").rsplit("/", 1)[-1]
                    definition = definitions.get(definition_key, None)

                    if not definition:
                        break

                    # Replace values with values in the definition.
                    property_values["title"] = camelized_key
                    property_values["type"] = definition.get("type", None)
                    definition_enum = definition.get("enum", None)
                    definition_properties = definition.get("properties", None)

                    if definition_enum:
                        field_type = schema_type_annotation.__fields__[key].type_
                        property_values["type"] = "enum"
                        property_values["enum"] = _format_enum_from_type(typ=field_type)

                    # If the schema references another schema, that definition will have
                    # a dict of its own properties. We want to flatten the form, and add
                    # these values, and remove the reference property.
                    if definition_properties:
                        properties_form_blocks = _build_form_blocks(
                            schema_type_annotation=schema_type_annotation,
                            schema_properties=definition_properties,
                            schema_definitions=None,
                            parent=camelized_key,
                        )
                        form_blocks.extend(properties_form_blocks)
                        # Do not include reference object, so continue to the next
                        # iteration.
                        raise SkipParentFormBlockCreationException
            except SkipParentFormBlockCreationException:
                continue

        property_values["element"] = FORM_ELEMENT_MAPPING[property_values["type"]]
        form_blocks.append(FormBlockRecord(id=camelized_key, **property_values))

    return form_blocks


def form_create_from_schema(
    *,
    schema: Schema,
    is_multipart_form: bool = False,
    sections: list[FormSectionRecord] | None = None,
) -> FormRecord | None:
    """
    Create a JSON form based on a defined schema.
    """

    sections = sections if sections is not None else []
    schema_type, schema_is_list = _validate_schema(schema=schema)

    if schema_type is None:
        return

    schema_definition = schema_type.schema()

    blocks = _build_form_blocks(
        schema_type_annotation=schema_type,
        schema_properties=schema_definition["properties"],
        schema_definitions=schema_definition.get("definitions", None),
        parent=None,
    )

    schema_required = schema_definition.get("required", [])
    required = [camelize(key) for key in schema_required]
    blocks_with_defaults = [
        block.id for block in blocks if block.default_value is not None
    ]

    # Only exclude fields with default as None from the required list, and not all
    # fields with set defaults.
    required = required + blocks_with_defaults

    return FormRecord(
        key=schema_definition["title"],
        is_multipart_form=is_multipart_form,
        expects_list=schema_is_list,
        required=required,
        sections=[
            FormSectionRecord(name=section.name, blocks=section.blocks)
            for section in sections
        ],
        blocks=blocks,
    )
