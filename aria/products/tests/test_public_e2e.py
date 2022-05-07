import json
import pytest
from model_bakery import baker
from aria.products.models import Product

from aria.users.tests.conftest import unauthenticated_client

pytestmark = pytest.mark.django_db

unauthenticated_client = unauthenticated_client


class TestPublicProductsEndpoints:

    base_endpoint = "/api/products"

    ###################
    # Detail endpoint #
    ###################

    def test_unauthenticated_user_products_retrieve(
        self, unauthenticated_client, django_assert_max_num_queries
    ):
        """
        Test that all attempts to get product detail returns a
        valid response.
        """

        product = baker.make(Product)

        expected_response = {
            "id": product.id,
            "status": product.get_status_display(),
            "unit": product.get_unit_display(),
            "name": product.name,
            "description": product.new_description,  # TODO: change to just description after we have migrated over.
            "images": [],
            "absorption": product.absorption,
            "materials": product.get_materials_display(),
            "rooms": product.get_rooms_display(),
            "supplier": product.supplier.name,
            "origin_country": product.supplier.origin_country,
            "available_in_special_sizes": product.available_in_special_sizes,
            "options": [],
            "colors": [],
            "shapes": [],
            "files": [],
        }

        # Get product  = 1
        # Get supplier = 1
        # Get images   = 1
        # Get options  = 1
        # Get colors   = 1
        # Get shapes   = 1
        # Get files    = 1
        # ----------------
        # Sum            7
        with django_assert_max_num_queries(7):
            response = unauthenticated_client.get(
                f"{self.base_endpoint}/product/{product.slug}/"
            )

        actual_response = json.loads(response.content)

        assert response.status_code == 200
        assert actual_response == expected_response
