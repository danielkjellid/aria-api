import json

import pytest

from aria.categories.tests.utils import create_category
from aria.products.enums import ProductUnit
from aria.products.tests.utils import create_product

pytestmark = pytest.mark.django_db


class TestPublicCategoriesEndpoints:

    BASE_ENDPOINT = "/api/categories"

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
                "list_images": {
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
                "list_images": {
                    "image500x305": sub_1.image500x305.url,
                    "image600x440": sub_1.image600x440.url,
                    "image850x520": sub_1.image850x520.url,
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
        cat_1 = create_category(name="Main cat 1")
        subcat_1 = create_category(name="Sub cat 1", parent=cat_1)
        products = create_product(quantity=20)

        for product in products:
            product.categories.set([subcat_1])

            for p in product.site_states.all():
                p.display_price = False
                p.gross_price = 500
                p.save()

        expected_response = [
            {
                "id": product.id,
                "name": product.name,
                "slug": product.slug,
                "unit": ProductUnit(product.unit).label,
                "thumbnail": product.thumbnail.url if product.thumbnail else None,
                "display_price": False,
                "from_price": "500.0",
                "colors": [
                    {"id": color.id, "name": color.name, "color_hex": color.color_hex}
                    for color in product.colors.all()
                ],
                "shapes": [
                    {"id": shape.id, "name": shape.name, "image": shape.image.id}
                    for shape in product.shapes.all()
                ],
                "materials": product.materials_display,
                "variants": [
                    {
                        "id": option.variant.id,
                        "name": option.variant.name,
                        "thumbnail": option.variant.thumbnail.url
                        if option.variant.thumbnail
                        else None,
                        "image": option.variant.image.id
                        if option.variant.image
                        else None,
                    }
                    for option in product.options.all()
                    if option.variant
                ],
            }
            for product in products
        ]

        # Uses 9 queries:
        # - 1 for getting related category,
        # - 1 for annotating display_price and from_price values,
        # - 1 for getting products,
        # - 1 for preloading product categories,
        # - 1 for preloading colors,
        # - 1 for preloading shapes,
        # - 1 for preloading images,
        # - 1 for preloading options,
        # - 1 for preloading files
        with django_assert_max_num_queries(9):
            response = anonymous_client.get(
                f"{self.BASE_ENDPOINT}/category/{subcat_1.slug}/products/"
            )

        actual_response = json.loads(response.content)

        assert response.status_code == 200
        assert actual_response == expected_response

        # Test that we fail gracefully by returning 404.
        # Uses 1 query by attempting to get category.
        with django_assert_max_num_queries(1):
            failed_response = anonymous_client.get(
                f"{self.BASE_ENDPOINT}/category/does-not-exist/products/"
            )

        assert failed_response.status_code == 404

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
