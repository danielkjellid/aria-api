import json
import tempfile

import pytest

from aria.suppliers.tests.utils import get_or_create_supplier

pytestmark = pytest.mark.django_db


class TestPublicSuppliersEndpoints:

    BASE_ENDPOINT = "/api/v1/suppliers"

    def test_anonymous_request_supplier_list(
        self, anonymous_client, django_assert_max_num_queries
    ) -> None:
        """
        Test listing suppliers from an anonymous client returns
        a valid response.
        """

        suppliers = [
            get_or_create_supplier(supplier_name="Supplier 1"),
            get_or_create_supplier(supplier_name="Supplier 2"),
            get_or_create_supplier(supplier_name="Supplier 3"),
            get_or_create_supplier(supplier_name="Supplier 4", is_active=False),
        ]

        for supplier in suppliers:
            with tempfile.NamedTemporaryFile(suffix=".jpg") as file:
                supplier.image = file.name
                supplier.save()

        with django_assert_max_num_queries(1):
            response = anonymous_client.get(f"{self.BASE_ENDPOINT}/")

        assert response.status_code == 200
        assert len(json.loads(response.content)) == 3  # 3 out of 4 active


class TestInternalSuppliersEndpoints:

    BASE_ENDPOINT = "/api/v1/internal/suppliers"

    def test_anonymous_request_supplier_list_internal_api(
        self, anonymous_client, django_assert_max_num_queries
    ):
        assert False

    def test_authenticated_unprivileged_request_supplier_list_internal_api(
        self, authenticated_unprivileged_client, django_assert_max_num_queries
    ):
        assert False

    def test_authenticated_privileged_request_supplier_list_internal_api(
        self, django_assert_max_num_queries, authenticated_privileged_client
    ):
        assert False
