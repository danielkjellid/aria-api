from ninja import Schema


class GenericResponse(Schema):
    message: str
    data: Schema


class ExceptionResponse(Schema):
    message: str
    extra: dict[str, str] = {}
