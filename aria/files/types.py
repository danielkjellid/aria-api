from typing import Any

from ninja.files import UploadedFile as NinjaUploadedFile
from pydantic.fields import ModelField


class UploadedFile(NinjaUploadedFile):
    @classmethod
    def __modify_schema__(
        cls, field_schema: dict[str, Any], field: ModelField | None
    ) -> None:
        field_schema.update(type="file", format="binary")


class UploadedImageFile(NinjaUploadedFile):
    @classmethod
    def __modify_schema__(
        cls, field_schema: dict[str, Any], field: ModelField | None
    ) -> None:
        field_schema.update(type="image", format="binary")
