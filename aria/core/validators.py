import os
from typing import Iterable

from django.core.files.images import ImageFile, get_image_dimensions
from django.core.files.uploadedfile import InMemoryUploadedFile, UploadedFile
from django.utils.translation import gettext as _

from aria.core.exceptions import ApplicationError


def image_validate(
    *,
    image: UploadedFile | InMemoryUploadedFile | ImageFile,
    allowed_extensions: Iterable[str],
    width_min_px: int | float,
    width_max_px: int | float,
    height_min_px: int | float,
    height_max_px: int | float,
) -> None:
    """
    Validate a single image's properties.
    """

    file_extension = None
    width, height = get_image_dimensions(image)

    if image.name is not None:
        _file_name, file_extension = os.path.splitext(image.name)

    if file_extension is not None and file_extension not in allowed_extensions:
        raise ApplicationError(
            message=_(
                "Image does not have a valid type. We only allow types ending with %s."
                % ", ".join(allowed_extensions)
            )
        )

    if width is not None and (width < width_min_px or width > width_max_px):
        raise ApplicationError(
            message=_(
                "Images should be in the range %(range)spx wide."
                % {"range": f"{width_min_px}-{width_max_px}"}
            )
        )

    if height is not None and (height < height_min_px or height > height_max_px):
        raise ApplicationError(
            message=_(
                "Images should be in the range %(range)spx high."
                % {"range": f"{height_min_px}-{height_max_px}"}
            )
        )
