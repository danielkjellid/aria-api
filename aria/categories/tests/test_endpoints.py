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
        pass

    def test_anonymous_request_category_products_list_api(
        self, anonymous_client, django_assert_max_num_queries
    ):
        pass

    def test_anonymous_request_category_detail_api(
        self, anonymous_client, django_assert_max_num_queries
    ):
        pass
