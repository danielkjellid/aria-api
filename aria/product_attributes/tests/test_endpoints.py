import pytest

from aria.product_attributes.tests.utils import create_shape

pytestmark = pytest.mark.django_db


class TestProductAttributesInternalEndpoints:

    BASE_ENDPOINT = "/api/v1/internal/product-attributes"

    ########################
    # Shapes list endpoint #
    ########################

    def test_endpoint_shape_list_internal_api(
        self,
        anonymous_client,
        authenticated_unprivileged_client,
        authenticated_unprivileged_staff_client,
        django_assert_max_num_queries,
        assert_client_response_is_status_code,
    ):
        """
        Test that staff users gets a valid response on listing all shapes and that all
        other request return appropriate HTTP status codes.
        """

        endpoint = f"{self.BASE_ENDPOINT}/shapes/"

        shape_1 = create_shape(name="Shape 1")
        shape_2 = create_shape(name="Shape 2")
        shape_3 = create_shape(name="Shape 3")
        shape_4 = create_shape(name="Shape 4")

        expected_response = [
            {
                "id": shape_4.id,
                "name": shape_4.name,
                "image": shape_4.image.url if shape_4.image else None,
            },
            {
                "id": shape_3.id,
                "name": shape_3.name,
                "image": shape_3.image.url if shape_3.image else None,
            },
            {
                "id": shape_2.id,
                "name": shape_2.name,
                "image": shape_2.image.url if shape_2.image else None,
            },
            {
                "id": shape_1.id,
                "name": shape_1.name,
                "image": shape_1.image.url if shape_1.image else None,
            },
        ]

        # Anonymous users should get 401.
        assert_client_response_is_status_code(
            client=anonymous_client,
            endpoint=endpoint,
            max_allowed_queries=0,
            expected_status_code=401,
        )

        # Authenticated users without the correct permissions should get 401.
        assert_client_response_is_status_code(
            client=authenticated_unprivileged_client,
            endpoint=endpoint,
            max_allowed_queries=1,
            expected_status_code=401,
        )

        # Staff users should get a valid response regardless of permissions.
        with django_assert_max_num_queries(2):
            response = authenticated_unprivileged_staff_client.get(
                endpoint,
                content_type="application/json",
            )

        assert response.status_code == 200
        assert len(response.json()) == 4
        assert response.json() == expected_response
