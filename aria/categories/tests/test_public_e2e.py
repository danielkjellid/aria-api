import json
import pytest
from model_bakery import baker

from aria.categories.models import Category
from aria.categories.selectors import (
    categories_children_active_list,
    categories_navigation_active_list,
    categories_parent_active_list,
)
from aria.products.models import Product
from aria.products.selectors import product_list_by_category

from aria.users.tests.conftest import unauthenticated_client

pytestmark = pytest.mark.django_db

unauthenticated_client = unauthenticated_client


class TestPublicCategoriesEndpoints:

    base_endpoint = "/api/categories/"

    #################
    # List endpoint #
    #################

    def test_unauthenticated_user_categories_list(
        self, unauthenticated_client, django_assert_max_num_queries
    ):
        """
        Test that all attempts to get categories returns a
        valid response.
        """

        baker.make(Category, _quantity=5)

        # Get the qs explicitly to refresh cache
        categories = categories_navigation_active_list()

        expected_response = [
            {
                "id": category.id,
                "name": category.name,
                "slug": category.slug,
                "ordering": category.ordering,
                "children": [],
            }
            for category in categories
        ]

        with django_assert_max_num_queries(1):
            response = unauthenticated_client.get(self.base_endpoint)

        actual_response = json.loads(response.content)

        assert response.status_code == 200
        assert actual_response == expected_response

    #########################
    # Parents list endpoint #
    #########################

    def test_unauthenticated_user_categories_parents_list(
        self, unauthenticated_client, django_assert_max_num_queries
    ):
        """
        Test that all attempts to get parent categories returns a
        valid response.
        """

        baker.make(Category, _quantity=5)

        # Get the qs explicitly to refresh cache
        categories = categories_parent_active_list()

        expected_response = [
            {
                "id": category.id,
                "name": category.name,
                "slug": category.slug,
                "ordering": category.ordering,
                "images": [],
            }
            for category in categories
        ]

        with django_assert_max_num_queries(1):
            response = unauthenticated_client.get(f"{self.base_endpoint}parents/")

        actual_response = json.loads(response.content)

        assert response.status_code == 200
        assert actual_response == expected_response

    ##################################
    # Parents children list endpoint #
    ##################################

    def test_unauthenticated_user_categories_parent_children_list(
        self, unauthenticated_client, django_assert_max_num_queries
    ):
        """
        Test that all attempts to get children categories returns a
        valid response.
        """

        category = baker.make(Category)
        subcategory = baker.make(Category, _quantity=5, **{"parent": category})

        categories = categories_children_active_list(parent=category)

        expected_response = [
            {
                "id": category.id,
                "name": category.name,
                "slug": category.slug,
                "ordering": category.ordering,
                "description": category.description,
                "images": {
                    "image500x305": category.image500x305.url,
                    "image600x440": category.image600x440.url,
                    "image850x520": category.image850x520.url,
                },
            }
            for category in categories
        ]

        with django_assert_max_num_queries(2):
            response = unauthenticated_client.get(
                f"{self.base_endpoint}{category.slug}/children/"
            )

        actual_response = json.loads(response.content)

        assert response.status_code == 200
        assert actual_response == expected_response

    ###################################
    # Category products list endpoint #
    ###################################

    def test_unauthenticated_user_categories_category_products_list(
        self, unauthenticated_client, django_assert_max_num_queries
    ):
        """
        Test that all attempts to get products list from category
        returns a valid response.
        """

        category = baker.make(Category)
        subcategory = baker.make(Category, **{"parent": category})
        created_products = baker.make(Product, _quantity=5)

        for product in created_products:
            product.categories.add(subcategory)
            product.save()

        products = product_list_by_category(category=category, filters=None)

        expected_response = [
            {
                "id": product.id,
                "name": product.name,
                "slug": product.slug,
                "unit": product.get_unit_display(),
                "thumbnail": product.thumbnail.url,
                "display_price": product.display_price,
                "from_price": product.get_lowest_option_price(),
                "colors": [],
                "shapes": [],
                "materials": [],
            }
            for product in products
        ]

        with django_assert_max_num_queries(3):
            response = unauthenticated_client.get(
                f"{self.base_endpoint}{category.slug}/products/"
            )

        actual_response = json.loads(response.content)

        assert response.status_code == 200
        assert actual_response == expected_response

    ###################
    # Detail endpoint #
    ###################

    def test_unauthenticated_user_categories_retrieve(
        self, unauthenticated_client, django_assert_max_num_queries
    ):
        """
        Test that all attempts to get a single category returns a
        valid response.
        """

        category = baker.make(Category)

        expected_response = {
            "id": category.id,
            "name": category.name,
        }

        with django_assert_max_num_queries(1):
            response = unauthenticated_client.get(
                f"{self.base_endpoint}{category.slug}/"
            )

        actual_response = json.loads(response.content)

        assert response.status_code == 200
        assert actual_response == expected_response
