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

        # When exceptions are raised and handled through exception handlers, the data
        # content is not rendered from pydantic to dict automatically, so therefore
        # we try to access the .dict() method of the returned pydantic model before
        # falling back to data.
        try:
            data_to_render = data.dict()
        except AttributeError:
            data_to_render = data

        return orjson.dumps(data_to_render)


class CamelCaseRenderer(BaseRenderer):
    """
    Render that renders data as camel case, and uses orjson to parse it.
    """

    media_type = "application/json"

    def render(self, request: HttpRequest, data: Any, *, response_status: int) -> Any:
        camelized_data = camelize(data)
        return orjson.dumps(camelized_data)
