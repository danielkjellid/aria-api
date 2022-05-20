import logging
from pathlib import Path

from django.apps import AppConfig
from django.conf import settings
from django.core.management import call_command

logger = logging.getLogger(__name__)


class ApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "aria.api"

    def ready(self) -> None:
        if not getattr(settings, "OPENAPI_AUTO_GENERATE", False):
            return

        openapi_schema_path_setting = getattr(settings, "OPENAPI_SCHEMA_PATH", None)

        if not openapi_schema_path_setting:
            base_path = getattr(settings, "BASE_DIR")
            folder_path = base_path / Path("../aria-frontend/@types/").resolve()
        else:
            folder_path = openapi_schema_path_setting

        # Make sure folder exist.
        folder_path.mkdir(parents=True, exist_ok=True)
        path = folder_path / "schema.json"

        with open(path, "w"):
            call_command(
                "export_openapi_schema", api="aria.urls.endpoints", output=path
            )
            logger.info(f"Wrote OpenAPI schema to {path}")
