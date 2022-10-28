import os
from typing import Iterable

from django.core.files.images import ImageFile, get_image_dimensions
from django.core.files.uploadedfile import InMemoryUploadedFile, UploadedFile
from django.utils.translation import gettext as _

import structlog

from aria.core.exceptions import ApplicationError

logger = structlog.get_logger(__name__)


def image_validate(
    *,
    image: UploadedFile | InMemoryUploadedFile | ImageFile,
    allowed_extensions: Iterable[str],
    width_min_px: int | float | None = None,
    width_max_px: int | float | None = None,
    height_min_px: int | float | None = None,
    height_max_px: int | float | None = None,
) -> None:
    """
    Validate a single image's properties.
    """

    image_extension = None
    image_name = None
    width, height = get_image_dimensions(image)

    if image.name is not None:
        image_name, image_extension = os.path.splitext(image.name)

    if image_extension is not None and image_extension not in allowed_extensions:
        raise ApplicationError(
            message=_(
                "Image does not have a valid type. We only allow types ending with %s."  # pylint: disable=C0209, line-too-long
                % ", ".join(allowed_extensions)
            )
        )

    if width_max_px is not None and width_min_px is not None:
        if width is not None and (width < width_min_px or width > width_max_px):
            raise ApplicationError(
                message=_(
                    "Images should be in the range %(range)spx wide."  # pylint: disable=C0209, line-too-long
                    % {"range": f"{width_min_px}-{width_max_px}"}
                )
            )

        logger.warn("Unable to validate image width.", image=image_name)

    if height_max_px is not None and height_min_px is not None:
        if height is not None and (height < height_min_px or height > height_max_px):
            raise ApplicationError(
                message=_(
                    "Images should be in the range %(range)spx high."  # pylint: disable=C0209, line-too-long
                    % {"range": f"{height_min_px}-{height_max_px}"}
                )
            )

        logger.warn("Unable to validate image height.", image=image_name)
