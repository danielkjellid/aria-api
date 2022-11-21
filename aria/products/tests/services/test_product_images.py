from unittest.mock import ANY

import pytest

from aria.files.tests.utils import create_image_file
from aria.products.records import ProductImageRecord
from aria.products.services.product_images import product_image_create
from aria.products.tests.utils import create_product

pytestmark = pytest.mark.django_db


class TestProductImagesServices:
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
