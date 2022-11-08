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


def image_resize(
    *,
    image: ImageFile | InMemoryUploadedFile | UploadedFile | TemporaryUploadedFile,
    max_width: int,
    max_height: int,
) -> ImageFile | InMemoryUploadedFile | UploadedFile | TemporaryUploadedFile:
    """
    Resize an image. This will both up- and downscale the image while maintaining aspect
    ratio. Meaning, that given the size 2048x1150, and max_width=1000, max_height=1000,
    the image will be scaled to 1000x688 (to maintain aspect ratio).
    """

    image_width, image_height = get_image_dimensions(image)
    size = (max_width, max_height)

    print("FIRED")

    # If image is already the required size, shortcircuit and return early.
    if image_width == max_width and image_height == max_height:
        return image

    # Uploaded file is in memory.
    if isinstance(image, (InMemoryUploadedFile, UploadedFile)):
        if image and image.name:
            memory_image = BytesIO(image.read())
            pil_image = PilImage.open(memory_image)
            img_format = os.path.splitext(image.name)[1][1:].upper()
            img_format = "JPEG" if img_format == "JPG" else img_format

            if pil_image.width > max_width or pil_image.height > max_height:
                pil_image.thumbnail(size)

            new_image = BytesIO()
            pil_image.save(new_image, format=img_format)

            new_image = ContentFile(new_image.getvalue())  # type: ignore

            return InMemoryUploadedFile(
                file=new_image,
                field_name=None,
                name=image.name,
                content_type=image.content_type,
                size=None,
                charset=None,
            )

    # Uploaded file is already on temp-disk.
    elif isinstance(image, TemporaryUploadedFile):
        path = image.temporary_file_path()
        pil_image = PilImage.open(path)

        if pil_image.width > max_width or pil_image.height > max_height:
            pil_image.thumbnail(size)
            pil_image.save(path)
            image.size = os.stat(path).st_size

    # Uploaded file is already on disk.
    elif isinstance(image, ImageFile):
        path = image.path  # type: ignore
        pil_image = PilImage.open(path)

        if pil_image.width > max_width or pil_image.height > max_height:
            pil_image.thumbnail(size)
            pil_image.save(path)

    return image
