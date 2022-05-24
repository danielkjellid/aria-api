from typing import Any, TypedDict


class ChangeMessage(TypedDict):
    field: str
    old_value: Any
    new_value: Any
