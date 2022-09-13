from typing import Callable, Sequence, Union

from ninja import NinjaAPI, Router
from ninja.constants import NOT_SET, NOT_SET_TYPE
from ninja.operation import Operation
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
        self.auth = auth  # type: ignore
        self.docs_decorator = docs_decorator

    def get_operation_url_name(self, operation: "Operation", router: Router) -> str:
        """
        Override to match path parameters instead of view function name.
        """

        router_tag = self._get_and_validate_router_tag(tags=operation.tags)
        formatted_path = operation.path.replace("/", "-").rstrip("-")
        url_name = f"{router_tag}-{formatted_path}"

        # If the name ends with a "-", it means that we're dealing
        # with an index, in that case, add a trailing index to it.
        if url_name.endswith("-"):
            url_name = f"{url_name}index"

        return url_name

    def _get_and_validate_router_tag(self, tags: list[str] | None) -> str:
        """
        Check that there is only a single tag provided.
        """

        if tags is None:
            raise NotImplementedError(
                'Router object must have a defined tag: Router(tags=["..."])'
            )

        if isinstance(tags, list):
            if len(tags) > 1:
                raise ValueError("Router object must only have one tag!")

        return tags[0].lower()
