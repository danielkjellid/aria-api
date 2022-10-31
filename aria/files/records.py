from __future__ import annotations

from datetime import datetime
from typing import TypeVar

from pydantic import BaseModel

from aria.files.models import BaseCollectionListImageModel, BaseHeaderImageModel

T_IMAGE_HEADER = TypeVar("T_IMAGE_HEADER", bound=BaseHeaderImageModel)
T_IMAGE_COLLECTION_LIST = TypeVar(
    "T_IMAGE_COLLECTION_LIST", bound=BaseCollectionListImageModel
)


class BaseHeaderImageRecord(BaseModel):
    image_url: str
    is_main_image: bool
    apply_filter: bool
    image1440x810_url: str
    image1280x720_url: str
    image1024x576_url: str
    image960x540_url: str
    image768x432_url: str
    image640x360_url: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_image(cls, image: T_IMAGE_HEADER) -> BaseHeaderImageRecord:
        return cls(
            image_url=image.image_url,
            is_main_image=image.is_main_image,
            apply_filter=image.apply_filter,
            image1440x810_url=image.image1440x810_url,
            image1280x720_url=image.image1280x720_url,
            image1024x576_url=image.image1024x576_url,
            image960x540_url=image.image960x540_url,
            image768x432_url=image.image768x432_url,
            image640x360_url=image.image640x360_url,
            created_at=image.created_at,
            updated_at=image.updated_at,
        )


class BaseCollectionListImageRecord(BaseModel):
    image_url: str
    image960x540: str
    image576x324: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_image(
        cls, image: T_IMAGE_COLLECTION_LIST
    ) -> BaseCollectionListImageRecord:
        return cls(
            image_url=image.image_url,
            image960x540_url=image.image960x540_url,
            image576x324=image.image576x324_url,
            created_at=image.created_at,
            updated_at=image.updated_at,
        )
