from typing import Any

from django.http import HttpRequest

import orjson
from ninja.parser import Parser

from aria.core.humps import decamelize, is_camelcase


class ORJSONParser(Parser):
    """
    A parser that parses data with orjson.
    """

    def parse_body(self, request: HttpRequest) -> Any:
        return orjson.loads(request.body)


class CamelCaseParser(Parser):
    """
    A parser that parses data from camel case to snake case,
    if the data sent is camel case. If not, it returnes parsed
    data with orjson.
    """

    def parse_body(self, request: HttpRequest) -> Any:
        data = orjson.loads(request.body)

        if is_camelcase(data):
            decamelized_data = decamelize(data)
            return decamelized_data

        return data
