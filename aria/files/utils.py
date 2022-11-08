from __future__ import annotations

import os
from io import BytesIO
from typing import TYPE_CHECKING, TypeVar

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.images import ImageFile, get_image_dimensions
from django.core.files.uploadedfile import (
    InMemoryUploadedFile,
    TemporaryUploadedFile,
    UploadedFile,
)
from django.utils.text import slugify

from libthumbor import CryptoURL
from PIL import Image as PilImage

if TYPE_CHECKING:
    from aria.files.models import BaseImageModel

    T_BASE_IMAGE_MODEL = TypeVar("T_BASE_IMAGE_MODEL", bound=BaseImageModel)

crypto_url = CryptoURL(key=settings.THUMBOR_SECURITY_KEY)


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


def image_generate_signed_url(
    *, image_name: str, width: int | None = None, height: int | None = None
) -> str:
    """
    Generate a thumbor signed image url.
    """

    thumbor_server_url = settings.THUMBOR_SERVER_URL.rstrip("/")
    # The media prefix is a temporary quick fix while we fix image paths.
    signed_url = crypto_url.generate(
        image_url=image_name, width=width, height=height, smart=True
    ).strip("/")

    return f"{thumbor_server_url}/{signed_url}"
