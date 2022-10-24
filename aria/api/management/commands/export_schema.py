import json
from typing import Any

from django.core.management.base import BaseCommand, CommandError, CommandParser
from django.utils.module_loading import import_string

from ninja.openapi.schema import OpenAPISchema
from packaging import version

from aria.api.base import AriaAPI


class Command(BaseCommand):

    help = "Export Open API schema"

    def _get_api_instance(self, *, api_path: str | None = None) -> AriaAPI:
        try:
            api = import_string(api_path)
        except ImportError as exc:
            raise CommandError(
                f"Module or attribute for {api_path} not found!"
            ) from exc

        if not isinstance(api, AriaAPI):
            raise CommandError(f"{api_path} is not instance of AriaAPI!")

        return api

    def _merge_schemas(self, *, apis: list[AriaAPI]) -> OpenAPISchema:

        schema: OpenAPISchema = {
            "openapi": None,
            "info": {
                "title": "Aria API",
                "version": None,
                "description": "",
            },
            "paths": {},
            "components": {},
        }

        # Merge paths and components across schemas.
        for api in apis:
            api_schema = api.get_openapi_schema()

            schema["openapi"] = api_schema["openapi"]
            schema["paths"].update(api_schema["paths"])
            schema["components"].update(api_schema["components"])

            # Set the version if it's empty or if the version in the current iteration
            # is higher than the one already set.
            if schema["info"]["version"] is None or (
                version.parse(schema["info"]["version"])
                < version.parse(api_schema["info"]["version"])
            ):
                schema["info"]["version"] = api_schema["info"]["version"]

        return schema

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--output", dest="output", default=None, type=str)

    def handle(self, *args: Any, **options: Any) -> None:

        api_v1 = self._get_api_instance(api_path="aria.urls.api_v1")
        api_v1_internal = self._get_api_instance(api_path="aria.urls.api_v1_internal")

        schema = self._merge_schemas(apis=[api_v1, api_v1_internal])
        result = json.dumps(schema, indent=None, sort_keys=False)

        if options["output"]:
            with open(options["output"], "wb") as f:
                f.write(result.encode())
        else:
            self.stdout.write(result)
