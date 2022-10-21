from django.core.files.uploadedfile import SimpleUploadedFile

import pytest

from aria.products.services.product_files import product_file_create
from aria.products.tests.utils import create_product

pytestmark = pytest.mark.django_db


class TestProductFilesServices:
    def test_service_product_file_create(self, django_assert_max_num_queries):
        """
        Test that the product_file_create service creates a product file within query
        limits.
        """

        product = create_product()
        product_file = SimpleUploadedFile("manual.pdf", b"data123")

        with django_assert_max_num_queries(1):
            created_file = product_file_create(
                product=product, name="Manual", file=product_file
            )

        assert created_file.name == "Manual"
        assert created_file.product_id == product.id
