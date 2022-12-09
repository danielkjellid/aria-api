from __future__ import annotations

import os
from typing import TYPE_CHECKING, TypeVar

from django.utils.text import slugify

if TYPE_CHECKING:
    from aria.files.models import BaseImageModel

    T_BASE_IMAGE_MODEL = TypeVar("T_BASE_IMAGE_MODEL", bound=BaseImageModel)


def asset_get_static_upload_path(instance: T_BASE_IMAGE_MODEL, filename: str) -> str:
    """
    Get the path of which to upload the image.
    """

    # Each image model is required to specify where images should be uploaded.
    try:
        path = instance.UPLOAD_PATH.lower()
    except AttributeError as exc:
        raise RuntimeError(
            f"UPLOAD_PATH is not set on model: {instance.__class__.__name__}"
        ) from exc

    name, extension = os.path.splitext(filename)

    return f"{path}/{slugify(name)}{extension}"
