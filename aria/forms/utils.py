from enum import Enum
from typing import Any

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


def form_create_from_schema(
    *,
    schema: Schema,
    is_multipart_form: bool = False,
    overrides: list[FormBlockRecord] | None = None,
    sections: list[FormSectionRecord] | None = None,
) -> FormRecord | None:
    """
    Create a JSON form based on a defined schema.
    """

    overrides = overrides if overrides is not None else []
    sections = sections if sections is not None else []

    schema_type, schema_is_list = _validate_schema(schema=schema)

    if schema_type is None:
        return

    def build_form(
        schema_properties: dict[str, Any],
        schema_definitions: dict[str, Any] | None,
        parent: str | None = None,
    ) -> list[FormBlockRecord]:
        form_blocks = []

        for key, value in schema_properties.items():
            title: str = value.get("title", None)
            typ: str = value.get("type", None)
            enum: list[FormBlockEnumRecord] | None = None
            default: str | int | bool | None = value.get("default", None)
            placeholder: str | None = None
            format_val: str = value.get("format", None)

            if format_val == "binary":
                typ = "file"

            value_ref = value.get("$ref", None)
            value_all_of_ref = value.get("allOf", [{}])[0].get("$ref", None)

            if value_ref:
                ref = value_ref
            elif value_all_of_ref:
                ref = value_all_of_ref
            else:
                ref = None

            if ref and schema_definitions:
                # Get the typename from the reference and find it in the definitions' dict.
                ref_from_value = ref.rsplit("/", 1)[-1]
                definition = schema_definitions.get(ref_from_value)

                # Replace values with values in the definition.
                title = definition.get("title", title)
                typ = definition.get("type", "enum")
                default = definition.get("default", default)
                enum_from_definition = definition.get("enum", None)
                properties = definition.get("properties", None)

                if enum_from_definition:
                    field_type = schema_type.__fields__[key].type_
                    enum = _format_enum_from_type(typ=field_type)

                # If the schema references another schema, that definition will have
                # a dict of its own properties. We want to flatten the form, and add
                # these values, and remove the reference property.
                if properties:
                    property_blocks = build_form(
                        schema_properties=properties,
                        schema_definitions=None,
                        parent=key,
                    )
                    form_blocks.extend(property_blocks)
                    # Do not include reference object, so continue to the next
                    # iteration.
                    continue

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
                parent=parent,
                default_value=overrides_dict.get("default_value", default),
                element=overrides_dict.get("element", element),
                placeholder=overrides_dict.get("placeholder", placeholder),
                help_text=overrides_dict.get("help_text", None),
                display_word_count=overrides_dict.get("display_word_count", False),
                hidden_label=overrides_dict.get("hidden_label", False),
                col_span=overrides_dict.get("col_span", None),
            )

            form_blocks.append(block)
        return form_blocks

    schema_definition = schema_type.schema()
    blocks = build_form(
        schema_properties=schema_definition["properties"],
        schema_definitions=schema_definition.get("definitions", None),
    )

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
