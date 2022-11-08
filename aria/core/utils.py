from typing import Any

from aria.core.records import BaseArrayFieldLabelRecord


def get_array_field_labels(
    choices: Any | None, enum: Any
) -> list[BaseArrayFieldLabelRecord]:
    """
    Return a list of human-readable labels for ArrayChoiceFields
    """

    if choices is None:
        return []

    return [
        BaseArrayFieldLabelRecord(name=item.label)
        for item in enum
        for choice in choices
        if item.value == choice and item.label
    ]
