from ninja import Schema


class APIResponse(Schema):
    message: str = None
    data: list[Schema] | Schema = {}


class ExceptionResponse(Schema):
    message: str
    extra: dict[str, str] = {}
