from django.core.files.uploadedfile import SimpleUploadedFile

import pytest

from aria.core.exceptions import ApplicationError
from aria.core.tests.utils import create_image_file
from aria.core.validators import image_validate


class TestCoreValidators:
    def test_validator_image_validate(self):
        """
        Test that the image_validate correctly validates image properties.
        """

        pdf_file = SimpleUploadedFile("file.pdf", b"")
        image = create_image_file(
            name="image", extension="jpeg", width=2048, height=1150
        )

        # Wrong filetype.
        with pytest.raises(ApplicationError):
            image_validate(image=pdf_file, allowed_extensions=[".jpg", ".jpeg"])

        # Image is too wide
        with pytest.raises(ApplicationError):
            image_validate(
                image=image,
                allowed_extensions=[".jpg", ".jpeg"],
                width_min_px=1000,
                width_max_px=2000,
                height_min_px=1000,
                height_max_px=2000,
            )

        # Image is too tall
        with pytest.raises(ApplicationError):
            image_validate(
                image=image,
                allowed_extensions=[".jpg", ".jpeg"],
                width_min_px=2000,
                width_max_px=2100,
                height_min_px=900,
                height_max_px=1000,
            )

        # Everything correct, should not raise any exceptions.
        image_validate(
            image=image,
            allowed_extensions=[".jpg", ".jpeg"],
            width_min_px=2000,
            width_max_px=2048,
            height_min_px=1000,
            height_max_px=1150,
        )
