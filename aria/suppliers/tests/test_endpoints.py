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

        get_or_create_supplier(supplier_name="Supplier 1")
        get_or_create_supplier(supplier_name="Supplier 2")
        get_or_create_supplier(supplier_name="Supplier 3")
        get_or_create_supplier(supplier_name="Supplier 4", is_active=False)

        with django_assert_max_num_queries(1):
            response = anonymous_client.get(f"{self.BASE_ENDPOINT}/")

        assert response.status_code == 200
        assert len(response.json()) == 3  # 3 out of 4 active


class TestInternalSuppliersEndpoints:

    BASE_ENDPOINT = "/api/v1/internal/suppliers"

    def test_endpoint_supplier_list_internal_api(
        self,
        anonymous_client,
        authenticated_unprivileged_client,
        authenticated_unprivileged_staff_client,
        django_assert_max_num_queries,
        assert_client_response_is_status_code,
    ):
        """
        Test that the supplier_list_internal_api endpoint returns an expected output
        for staff users, and returns correct HTTP error codes for non-staff users.
        """

        endpoint = f"{self.BASE_ENDPOINT}/"

        supplier_1 = get_or_create_supplier(supplier_name="Supplier 1")
        supplier_2 = get_or_create_supplier(supplier_name="Supplier 2")
        supplier_3 = get_or_create_supplier(supplier_name="Supplier 3")
        supplier_4 = get_or_create_supplier(supplier_name="Supplier 4", is_active=False)

        expected_output = [
            {"id": supplier_1.id, "name": "Supplier 1", "isActive": True},
            {"id": supplier_2.id, "name": "Supplier 2", "isActive": True},
            {"id": supplier_3.id, "name": "Supplier 3", "isActive": True},
            {"id": supplier_4.id, "name": "Supplier 4", "isActive": False},
        ]

        # Anonymous users should get 401.
        assert_client_response_is_status_code(
            client=anonymous_client,
            endpoint=endpoint,
            max_allowed_queries=0,
            expected_status_code=401,
        )

        # Authenticated users which are not staff should get 401.
        assert_client_response_is_status_code(
            client=authenticated_unprivileged_client,
            endpoint=endpoint,
            max_allowed_queries=1,
            expected_status_code=401,
        )

        with django_assert_max_num_queries(2):
            response = authenticated_unprivileged_staff_client.get(endpoint)

        assert response.status_code == 200
        assert response.json() == expected_output
