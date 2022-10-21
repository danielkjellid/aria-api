from typing import TypedDict


class PydanticErrorDict(TypedDict):
    loc: tuple[int | str, ...]
    msg: str
    type: str
