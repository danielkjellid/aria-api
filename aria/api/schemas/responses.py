from typing import Any

from ninja import Schema


class ExceptionResponse(Schema):
    message: str
    extra: dict[str, Any] = {}
