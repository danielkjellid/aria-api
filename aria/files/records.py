from __future__ import annotations

from typing import TypeVar

from pydantic import BaseModel

from aria.files.models import BaseCollectionListImageModel, BaseHeaderImageModel

T_IMAGE_HEADER = TypeVar("T_IMAGE_HEADER", bound=BaseHeaderImageModel)
T_IMAGE_COLLECTION_LIST = TypeVar(
    "T_IMAGE_COLLECTION_LIST", bound=BaseCollectionListImageModel
)


class BaseHeaderImageRecord(BaseModel):
    is_main_image: bool
    apply_filter: bool
    image_url: str | None
    image1440x810_url: str | None
    image1280x720_url: str | None
    image1024x576_url: str | None
    image960x540_url: str | None
    image768x432_url: str | None
    image640x360_url: str | None

    @classmethod
    def from_model(cls, model: T_IMAGE_HEADER) -> BaseHeaderImageRecord:
        """
        Generate record from model.
        """
        return cls(
            image_url=model.image_url,
            is_main_image=model.is_main_image,
            apply_filter=model.apply_filter,
            image1440x810_url=model.image1440x810_url,
            image1280x720_url=model.image1280x720_url,
            image1024x576_url=model.image1024x576_url,
            image960x540_url=model.image960x540_url,
            image768x432_url=model.image768x432_url,
            image640x360_url=model.image640x360_url,
        )


class BaseCollectionListImageRecord(BaseModel):
    image_url: str | None
    image960x540_url: str | None
    image576x324_url: str | None

    @classmethod
    def from_model(
        cls, model: T_IMAGE_COLLECTION_LIST
    ) -> BaseCollectionListImageRecord:
        """
        Generate record from model.
        """
        return cls(
            image_url=model.image_url,
            image960x540_url=model.image960x540_url,
            image576x324_url=model.image576x324_url,
        )
