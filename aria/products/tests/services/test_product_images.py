from unittest.mock import ANY

from django.core.files.uploadedfile import SimpleUploadedFile

import pytest

from aria.core.exceptions import ApplicationError
from aria.core.tests.utils import create_image_file
from aria.products.records import ProductImageRecord
from aria.products.services.product_images import product_image_create
from aria.products.tests.utils import create_product

pytestmark = pytest.mark.django_db


class TestProductImagesServices:
    # def test_service__validate_product_image(self):
    #     """
    #     Test that the validate_product_image correctly validates image properties.
    #     """
    #
    #     pdf_file = SimpleUploadedFile("file.pdf", b"")
    #     image_too_narrow = create_image_file(
    #         name="too-narrow", extension="jpeg", width=100, height=860
    #     )
    #     image_too_small = create_image_file(
    #         name="too-small", extension="jpeg", width=1536, height=50
    #     )
    #     image = create_image_file(
    #         name="right-aspect", extension="jpeg", width=2048, height=1150
    #     )
    #
    #     # Wrong filetype.
    #     with pytest.raises(ApplicationError):
    #         _validate_product_image(image=pdf_file)
    #
    #     # Not wide enough.
    #     with pytest.raises(ApplicationError):
    #         _validate_product_image(image=image_too_narrow)
    #
    #     # Not tall enough.
    #     with pytest.raises(ApplicationError):
    #         _validate_product_image(image=image_too_small)
    #
    #     # Everything correct, should not raise any exceptions.
    #     _validate_product_image(image=image)

    def test_service_product_image_create(self, django_assert_max_num_queries):
        """
        Test that the product_image_create service bulk creates an image within query
        limits.
        """

        product = create_product()
        product_image = create_image_file(
            name="image1", extension="jpeg", width=2048, height=1150
        )

        assert product.images.count() == 0

        with django_assert_max_num_queries(1):
            created_image = product_image_create(product=product, image=product_image)

        assert created_image.product_id == product.id
        assert product.images.count() == 1
        assert created_image == ProductImageRecord.construct(
            id=ANY, product_id=product.id, image_url=ANY
        )
