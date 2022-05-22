import json

import pytest

from aria.categories.tests.utils import create_category

pytestmark = pytest.mark.django_db


class TestPublicCategoriesEndpoints:

    BASE_ENDPOINT = "/api/ninja/categories"

    def test_anonymous_request_category_list_api(
        self, anonymous_client, django_assert_max_num_queries
    ):
        """
        Test listing categories from an anonymous client returns
        a valid response.
        """

        main_cat_1 = create_category(name="Main cat 1")
        main_cat_1_sub_1 = create_category("Sub cat 1.1", parent=main_cat_1)
        main_cat_1_sub_2 = create_category("Sub cat 1.2", parent=main_cat_1)

        main_cat_2 = create_category(name="Main cat 2")
        main_cat_2_sub_1 = create_category("Sub cat 2.1", parent=main_cat_2)

        expected_payload = [
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
                        "children": [],
                    },
                    {
                        "id": main_cat_1_sub_2.id,
                        "name": main_cat_1_sub_2.name,
                        "slug": main_cat_1_sub_2.slug,
                        "ordering": main_cat_1_sub_2.ordering,
                        "children": [],
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
                        "children": [],
                    }
                ],
            },
        ]

        with django_assert_max_num_queries(3):
            response = anonymous_client.get(f"{self.BASE_ENDPOINT}/")

        actual_response = json.loads(response.content)

        assert response.status_code == 200
        assert len(actual_response) == 2
        assert actual_response == expected_payload

    def test_anonymous_request_category_parent_list_api(
        self, anonymous_client, django_assert_max_num_queries
    ):
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
                    "apply_filter": main_cat_1.apply_filter,
                    "image_512x512": main_cat_1.image_512x512.url,
                    "image_640x275": main_cat_1.image_640x275.url,
                    "image_1024x575": main_cat_1.image_1024x575.url,
                    "image_1024x1024": main_cat_1.image_1024x1024.url,
                    "image_1536x860": main_cat_1.image_1536x860.url,
                    "image_2048x1150": main_cat_1.image_2048x1150.url,
                },
            },
            {
                "id": main_cat_2.id,
                "name": main_cat_2.name,
                "slug": main_cat_2.slug,
                "ordering": main_cat_2.ordering,
                "images": {
                    "apply_filter": main_cat_2.apply_filter,
                    "image_512x512": main_cat_2.image_512x512.url,
                    "image_640x275": main_cat_2.image_640x275.url,
                    "image_1024x575": main_cat_2.image_1024x575.url,
                    "image_1024x1024": main_cat_2.image_1024x1024.url,
                    "image_1536x860": main_cat_2.image_1536x860.url,
                    "image_2048x1150": main_cat_2.image_2048x1150.url,
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
    ):
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
                "images": {
                    "apply_filter": sub_1.apply_filter,
                    "image_512x512": sub_1.image_512x512.url,
                    "image_640x275": sub_1.image_640x275.url,
                    "image_1024x575": sub_1.image_1024x575.url,
                    "image_1024x1024": sub_1.image_1024x1024.url,
                    "image_1536x860": sub_1.image_1536x860.url,
                    "image_2048x1150": sub_1.image_2048x1150.url,
                },
            },
            {
                "id": sub_2.id,
                "name": sub_2.name,
                "slug": sub_2.slug,
                "ordering": sub_2.ordering,
                "description": sub_2.description,
                "images": {
                    "apply_filter": sub_2.apply_filter,
                    "image_512x512": sub_2.image_512x512.url,
                    "image_640x275": sub_2.image_640x275.url,
                    "image_1024x575": sub_2.image_1024x575.url,
                    "image_1024x1024": sub_2.image_1024x1024.url,
                    "image_1536x860": sub_2.image_1536x860.url,
                    "image_2048x1150": sub_2.image_2048x1150.url,
                },
            },
        ]

        # Uses 2 queries: 1 for checking if category with procided slug
        # exist, and 1 for getting children.
        with django_assert_max_num_queries(2):
            response = anonymous_client.get(
                f"{self.BASE_ENDPOINT}/category/{cat_1.slug}/children/"
            )

        actual_response = json.loads(response.content)

        assert response.status_code == 200
        assert actual_response == expected_response

        # Test querying for a slug that does not exist returns a 404.
        with django_assert_max_num_queries(1):
            failed_response = anonymous_client.get(
                f"{self.BASE_ENDPOINT}/category/does-not-exist/children/"
            )
        assert failed_response.status_code == 404

    def test_anonymous_request_category_products_list_api(
        self, anonymous_client, django_assert_max_num_queries
    ):
        pass

    def test_anonymous_request_category_detail_api(
        self, anonymous_client, django_assert_max_num_queries
    ):
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
                "apply_filter": cat_1.apply_filter,
                "image_512x512": cat_1.image_512x512.url,
                "image_640x275": cat_1.image_640x275.url,
                "image_1024x575": cat_1.image_1024x575.url,
                "image_1024x1024": cat_1.image_1024x1024.url,
                "image_1536x860": cat_1.image_1536x860.url,
                "image_2048x1150": cat_1.image_2048x1150.url,
            },
        }

        # Uses 1 query for getting category
        with django_assert_max_num_queries(1):
            response = anonymous_client.get(
                f"{self.BASE_ENDPOINT}/category/{cat_1.slug}/"
            )

        actual_response = json.loads(response.content)

        assert response.status_code == 200
        assert actual_response == expected_response

        # Test querying for a slug that does not exist returns a 404.
        with django_assert_max_num_queries(1):
            failed_response = anonymous_client.get(
                f"{self.BASE_ENDPOINT}/category/does-not-exist/"
            )

        assert failed_response.status_code == 404
