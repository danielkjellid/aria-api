from typing import Any

from django.http import HttpRequest

import orjson
from ninja.renderers import BaseRenderer

from aria.core.humps import camelize


class ORJSONRenderer(BaseRenderer):
    """
    Rendrer that renders data using orjson instaead of regualar json.
    """

    media_type = "application/json"

    def render(self, request: HttpRequest, data: Any, *, response_status: int) -> Any:
        return orjson.dumps(data)


class CamelCaseRenderer(BaseRenderer):
    """
    Render that renders data as camel case, and uses orjson to parse it.
    """

    media_type = "application/json"

    def render(self, request: HttpRequest, data: Any, *, response_status: int) -> Any:
        camelized_data = camelize(data)
        return orjson.dumps(camelized_data)
