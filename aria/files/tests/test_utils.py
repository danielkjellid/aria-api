import base64
import hashlib
import hmac

import pytest

from aria.files.models import BaseImageModel
from aria.files.tests.utils import create_image_file
from aria.files.utils import asset_get_static_upload_path, image_generate_signed_url
from aria.products.tests.utils import create_product


class TestFilesUtils:
    def test_util_asset_get_static_upload_path(self):
        """
        Test that the asset_get_static_upload_path util correctly throws error and
        that output is as expected.
        """

        model = BaseImageModel

        with pytest.raises(RuntimeError):
            asset_get_static_upload_path(instance=model, filename="filename.jpg")

        model.UPLOAD_PATH = "folder/subfolder"
        path = asset_get_static_upload_path(instance=model, filename="filename.jpg")

        expected_upload_path = "folder/subfolder/filename.jpg"

        assert path == expected_upload_path

    @pytest.mark.django_db
    def test_util_image_generate_signed_url(
        self, settings, django_assert_max_num_queries
    ):
        """
        Test that the image_generate_signed_url correctly generates a thumbor signed
        url for the given dimensions.
        """

        security_key = settings.THUMBOR_SECURITY_KEY
        thumbor_server_url = settings.THUMBOR_SERVER_URL

        product = create_product()
        image_file = create_image_file(
            name="thumb", extension="JPEG", width=380, height=575
        )

        product.thumbnail = image_file
        product.save()

        assert product.thumbnail is not None

        image_name = product.thumbnail.name
        assert (
            image_name
            == "media/products/example-supplier/test-product-0/images/thumb.jpeg"
        )

        # Thumbor uses standard HMAC with SHA1 signing with the native base64 module to
        # encode an urlsafe string.
        url_path = bytes(f"300x300/smart/media/{image_name}".encode("utf-8"))
        key = bytes(security_key.encode("utf-8"))
        digester = hmac.new(key, url_path, hashlib.sha1)
        signature = digester.digest()

        url_safe_signature = base64.urlsafe_b64encode(signature).decode("ascii")

        expected_url = (
            f"{thumbor_server_url}/{url_safe_signature}/300x300/smart/"
            f"media/{image_name}"
        )

        with django_assert_max_num_queries(0):
            image_url = image_generate_signed_url(
                image_name=image_name, width=300, height=300
            )

        assert image_url == expected_url
