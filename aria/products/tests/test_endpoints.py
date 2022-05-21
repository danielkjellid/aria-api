import pytest
from aria.products.tests.utils import create_product
from aria.core.exceptions import ApplicationError

pytestmark = pytest.mark.django_db


class TestPublicProductsEndpoints:

    BASE_ENDPOINT = "/api/products"

    def test_anonymous_request_product_detail_api(
        self, anonymous_client, django_assert_max_num_queries
    ):
        """
        Test retrieving a singular product from an anonymous client returns
        a valid response.
        """

        product = create_product()

        # Test that we fail when an invalid slug is passed.
        with django_assert_max_num_queries(1):
            failed_response = anonymous_client.get(
                f"{self.BASE_ENDPOINT}/does-not-exist/"
            )

            assert failed_response.status_code == 404

        # Test that we return a valid response on existing slug.
        with django_assert_max_num_queries(12):
            response = anonymous_client.get(f"{self.BASE_ENDPOINT}/{product.slug}/")

        assert response.status_code == 200
