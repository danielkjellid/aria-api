import json

from django.core.cache import cache

import pytest

from aria.categories.tests.utils import create_category

pytestmark = pytest.mark.django_db


class TestPublicCategoriesEndpoints:

    BASE_ENDPOINT = "/api/v1/categories"

    def test_anonymous_request_category_list_api(
        self, anonymous_client, django_assert_max_num_queries
    ) -> None:
        """
        Test listing categories from an anonymous client returns
        a valid response.
        """

        cache.clear()

        main_cat_1 = create_category(name="Main cat 1")
        main_cat_1_sub_1 = create_category("Sub cat 1.1", parent=main_cat_1)
        main_cat_1_sub_2 = create_category("Sub cat 1.2", parent=main_cat_1)

        main_cat_2 = create_category(name="Main cat 2")
        main_cat_2_sub_1 = create_category("Sub cat 2.1", parent=main_cat_2)

        expected_response = [
            {
                "id": main_cat_1.id,
                "name": main_cat_1.name,
                "slug": main_cat_1.slug,
                "ordering": main_cat_1.ordering,
                "children": [
                    {
                        "id": main_cat_1_sub_1.id,
                        "name": main_cat_1_sub_1.name,
                        "slug": main_cat_1_sub_1.slug,
                        "ordering": main_cat_1_sub_1.ordering,
                        "children": None,
                    },
                    {
                        "id": main_cat_1_sub_2.id,
                        "name": main_cat_1_sub_2.name,
                        "slug": main_cat_1_sub_2.slug,
                        "ordering": main_cat_1_sub_2.ordering,
                        "children": None,
                    },
                ],
            },
            {
                "id": main_cat_2.id,
                "name": main_cat_2.name,
                "slug": main_cat_2.slug,
                "ordering": main_cat_2.ordering,
                "children": [
                    {
                        "id": main_cat_2_sub_1.id,
                        "name": main_cat_2_sub_1.name,
                        "slug": main_cat_2_sub_1.slug,
                        "ordering": main_cat_2_sub_1.ordering,
                        "children": None,
                    }
                ],
            },
        ]

        with django_assert_max_num_queries(3):
            response = anonymous_client.get(f"{self.BASE_ENDPOINT}/")

        actual_response = json.loads(response.content)

        assert response.status_code == 200
        assert len(actual_response) == 2
        assert actual_response == expected_response

    def test_anonymous_request_category_parent_list_api(
        self, anonymous_client, django_assert_max_num_queries
    ) -> None:
        """
        Test listing parent categories from an anonymous client returns
        a valid response.
        """

        main_cat_1 = create_category(name="Main cat 1")
        main_cat_2 = create_category(name="Main cat 2")

        # Create some subcategories to test that these is not
        # a part of the returned response.
        create_category("Sub cat 1.1", parent=main_cat_1)
        create_category("Sub cat 1.2", parent=main_cat_1)
        create_category("Sub cat 2.1", parent=main_cat_2)

        expected_response = [
            {
                "id": main_cat_1.id,
                "name": main_cat_1.name,
                "slug": main_cat_1.slug,
                "ordering": main_cat_1.ordering,
                "images": {
                    "applyFilter": main_cat_1.apply_filter,
                    "image512x512": main_cat_1.image_512x512.url,
                    "image640x275": main_cat_1.image_640x275.url,
                    "image1024x575": main_cat_1.image_1024x575.url,
                    "image1024x1024": main_cat_1.image_1024x1024.url,
                    "image1536x860": main_cat_1.image_1536x860.url,
                    "image2048x1150": main_cat_1.image_2048x1150.url,
                },
            },
            {
                "id": main_cat_2.id,
                "name": main_cat_2.name,
                "slug": main_cat_2.slug,
                "ordering": main_cat_2.ordering,
                "images": {
                    "applyFilter": main_cat_2.apply_filter,
                    "image512x512": main_cat_2.image_512x512.url,
                    "image640x275": main_cat_2.image_640x275.url,
                    "image1024x575": main_cat_2.image_1024x575.url,
                    "image1024x1024": main_cat_2.image_1024x1024.url,
                    "image1536x860": main_cat_2.image_1536x860.url,
                    "image2048x1150": main_cat_2.image_2048x1150.url,
                },
            },
        ]

        # Uses 1 query to get the categories.
        with django_assert_max_num_queries(1):
            response = anonymous_client.get(f"{self.BASE_ENDPOINT}/parents/")

        actual_response = json.loads(response.content)

        assert response.status_code == 200
        assert actual_response == expected_response

    def test_anonymous_request_category_children_list_api(
        self, anonymous_client, django_assert_max_num_queries
    ) -> None:
        """
        Test listing parent categories from an anonymous client returns
        a valid response.
        """

        cat_1 = create_category(name="Main cat 1")
        sub_1 = create_category("Sub cat 1.1", parent=cat_1)
        sub_2 = create_category("Sub cat 1.2", parent=cat_1)

        expected_response = [
            {
                "id": sub_1.id,
                "name": sub_1.name,
                "slug": sub_1.slug,
                "ordering": sub_1.ordering,
                "description": sub_1.description,
                "listImages": {
                    "image500x305": sub_1.image500x305.url,
                    "image600x440": sub_1.image600x440.url,
                    "image850x520": sub_1.image850x520.url,
                },
            },
            {
                "id": sub_2.id,
                "name": sub_2.name,
                "slug": sub_2.slug,
                "ordering": sub_2.ordering,
                "description": sub_2.description,
                "listImages": {
                    "image500x305": sub_1.image500x305.url,
                    "image600x440": sub_1.image600x440.url,
                    "image850x520": sub_1.image850x520.url,
                },
            },
        ]

        # Uses 2 queries: 1 for checking if category with provided slug
        # exist, and 1 for getting children.
        with django_assert_max_num_queries(2):
            response = anonymous_client.get(
                f"{self.BASE_ENDPOINT}/{cat_1.slug}/children/"
            )

        actual_response = json.loads(response.content)

        assert response.status_code == 200
        assert actual_response == expected_response

        # Test querying for a slug that does not exist returns a 404.
        with django_assert_max_num_queries(1):
            failed_response = anonymous_client.get(
                f"{self.BASE_ENDPOINT}/does-not-exist/children/"
            )
        assert failed_response.status_code == 404

    def test_anonymous_request_category_detail_api(
        self, anonymous_client, django_assert_max_num_queries
    ) -> None:
        """
        Test retrieving a specific category from an anonymous client returns
        a valid response.
        """

        cat_1 = create_category(name="Main cat 1")

        expected_response = {
            "id": cat_1.id,
            "name": cat_1.name,
            "slug": cat_1.slug,
            "images": {
                "applyFilter": cat_1.apply_filter,
                "image512x512": cat_1.image_512x512.url,
                "image640x275": cat_1.image_640x275.url,
                "image1024x575": cat_1.image_1024x575.url,
                "image1024x1024": cat_1.image_1024x1024.url,
                "image1536x860": cat_1.image_1536x860.url,
                "image2048x1150": cat_1.image_2048x1150.url,
            },
        }

        # Uses 1 query for getting category
        with django_assert_max_num_queries(1):
            response = anonymous_client.get(f"{self.BASE_ENDPOINT}/{cat_1.slug}/")

        actual_response = json.loads(response.content)

        assert response.status_code == 200
        assert actual_response == expected_response

        # Test querying for a slug that does not exist returns a 404.
        with django_assert_max_num_queries(1):
            failed_response = anonymous_client.get(
                f"{self.BASE_ENDPOINT}/does-not-exist/"
            )

        assert failed_response.status_code == 404


class TestInternalCategoriesEndpoints:

    BASE_ENDPOINT = "/api/v1/internal/categories"

    def test_endpoint_category_list_internal_api(
        self,
        anonymous_client,
        authenticated_unprivileged_client,
        authenticated_privileged_client,
        authenticated_unprivileged_staff_client,
        django_assert_max_num_queries,
        assert_client_response_is_status_code,
    ):
        """
        Test that the category_list_internal_api endpoint returns an expected output
        for staff users, and returns correct HTTP error codes for non-staff users.
        """

        endpoint = f"{self.BASE_ENDPOINT}/"

        cat_1 = create_category(name="Parent 1")
        cat_2 = create_category(name="Parent 2")

        subcat_1 = create_category(name="Child 1", parent=cat_1)
        subcat_2 = create_category(name="Child 2", parent=cat_1)
        subcat_3 = create_category(name="Child 3", parent=cat_1)
        subcat_4 = create_category(name="Child 4", parent=cat_2)
        subcat_5 = create_category(name="Child 5", parent=cat_2)
        subcat_6 = create_category(name="Child 6", parent=cat_2)

        expected_response = [
            {"id": subcat_1.id, "name": "Child 1", "displayName": "Parent 1 > Child 1"},
            {"id": subcat_2.id, "name": "Child 2", "displayName": "Parent 1 > Child 2"},
            {"id": subcat_3.id, "name": "Child 3", "displayName": "Parent 1 > Child 3"},
            {"id": subcat_4.id, "name": "Child 4", "displayName": "Parent 2 > Child 4"},
            {"id": subcat_5.id, "name": "Child 5", "displayName": "Parent 2 > Child 5"},
            {"id": subcat_6.id, "name": "Child 6", "displayName": "Parent 2 > Child 6"},
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

        # Staff users should get a valid response regardless of permissions.
        with django_assert_max_num_queries(2):
            response = authenticated_unprivileged_staff_client.get(
                endpoint,
                content_type="application/json",
            )

        assert response.status_code == 200
        assert len(response.json()) == 6
        assert response.json() == expected_response
