from typing import Callable, Sequence, Union

from ninja import NinjaAPI
from ninja.constants import NOT_SET, NOT_SET_TYPE
from ninja.types import TCallable

from aria.api.parsers import CamelCaseParser
from aria.api.renderers import CamelCaseRenderer


class AriaAPI(NinjaAPI):  # pylint: disable=too-many-instance-attributes
    """
    Base class to create APIs. Inherits Django Ninjas base NinjaAPI, but overrides
    default renders and parsers, as well as how url_namespaces are generated.
    """

    def __init__(
        self,
        *,
        title: str = "NinjaAPI",
        version: str = "1.0.0",
        description: str = "",
        docs_decorator: Callable[[TCallable], TCallable] | None = None,
        urls_namespace: str | None = None,
        auth: Union[Sequence[Callable], Callable, NOT_SET_TYPE] | None = NOT_SET,  # type: ignore # pylint: disable=line-too-long
    ):
        super().__init__()

        self.title = title
        self.version = version
        self.description = description
        self.urls_namespace = f"{urls_namespace}-{self.version}"
        self.renderer = CamelCaseRenderer()
        self.parser = CamelCaseParser()
        self.auth = auth
        self.docs_decorator = docs_decorator
