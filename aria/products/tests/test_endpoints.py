import json

import pytest

from aria.categories.tests.utils import create_category
from aria.products.enums import ProductStatus, ProductUnit
from aria.products.tests.utils import create_product

pytestmark = pytest.mark.django_db


class TestPublicProductsEndpoints:

    BASE_ENDPOINT = "/api/products"

    def test_anonymous_requesst_product_list_by_category_api(
        self, anonymous_client, django_assert_max_num_queries
    ):
        """
        Test listing products to a related category from an anonymous
        client returns a valid response.
        """
        cat_1 = create_category(name="Main cat 1")
        subcat_1 = create_category(name="Sub cat 1", parent=cat_1)
        products = create_product(quantity=20)

        for product in products:
            product.categories.set([subcat_1])

        expected_response = [
            {
                "id": product.id,
                "name": product.name,
                "slug": product.slug,
                "unit": ProductUnit(product.unit).label,
                "supplier": {
                    "name": product.supplier.name,
                    "origin_country": product.supplier.origin_country.name,
                    "origin_country_flag": product.supplier.origin_country.unicode_flag,
                },
                "thumbnail": product.thumbnail.url if product.thumbnail else None,
                "display_price": True,
                "from_price": 0.0,
                "colors": [
                    {"id": color.id, "name": color.name, "color_hex": color.color_hex}
                    for color in product.colors.all()
                ],
                "shapes": [
                    {"id": shape.id, "name": shape.name, "image": shape.image.id}
                    for shape in product.shapes.all()
                ],
                "materials": product.materials_display,
                "rooms": product.rooms_display,
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

        # Uses 8 queries:
        # - 1 for getting related category,
        # - 1 for getting products,
        # - 1 for preloading options,
        # - 1 for preloading product categories,
        # - 1 for preloading colors,
        # - 1 for preloading shapes,
        # - 1 for preloading images,
        # - 1 for preloading files
        with django_assert_max_num_queries(8):
            response = anonymous_client.get(
                f"{self.BASE_ENDPOINT}/category/{subcat_1.slug}/"
            )

            actual_response = json.loads(response.content)

            assert response.status_code == 200
            assert actual_response == expected_response

        # Test that we fail gracefully by returning 404.
        # Uses 1 query by attempting to get category.
        with django_assert_max_num_queries(1):
            failed_response = anonymous_client.get(
                f"{self.BASE_ENDPOINT}/category/does-not-exist/"
            )

            assert failed_response.status_code == 404

    def test_anonymous_request_product_detail_api(
        self, anonymous_client, django_assert_max_num_queries
    ) -> None:
        """
        Test retrieving a singular product from an anonymous client returns
        a valid response.
        """

        product = create_product()

        expected_response = {
            "id": product.id,
            "status": ProductStatus(product.status).label,
            "unit": ProductUnit(product.unit).label,
            "name": product.name,
            "description": product.new_description,
            "absorption": product.absorption,
            "materials": product.materials_display,
            "rooms": product.rooms_display,
            "available_in_special_sizes": product.available_in_special_sizes,
            "can_be_picked_up": product.can_be_picked_up,
            "can_be_purchased_online": product.can_be_purchased_online,
            "display_price": product.display_price,
            "from_price": product.from_price,
            "supplier": {
                "name": product.supplier.name,
                "origin_country": product.supplier.origin_country.name,
                "origin_country_flag": product.supplier.origin_country.unicode_flag,
            },
            "images": [
                {
                    "apply_filter": image.apply_filter,
                    "image_512x512": image.image_512x512.url,
                    "image_640x275": image.image_640x275.url,
                    "image_1024x575": image.image_1024x575.url,
                    "image_1024x1024": image.image_1024x1024.url,
                    "image_1536x860": image.image_1536x860.url,
                    "image_2048x1150": image.image_2048x1150.url,
                }
                for image in product.images.all()
            ],
            "options": [
                {
                    "id": option.id,
                    "gross_price": option.gross_price,
                    "status": ProductStatus(option.status).label,
                    "variant": {
                        "id": option.variant.id,
                        "name": option.variant.name,
                        "image": option.variant.image.url,
                        "is_standard": option.variant.is_standard,
                    }
                    if option.variant
                    else None,
                    "size": {
                        "id": option.size.id,
                        "name": option.size.name,
                    }
                    if option.size
                    else None,
                }
                for option in product.options.all()
            ],
            "colors": [
                {"name": color.name, "color_hex": color.color_hex}
                for color in product.colors.all()
            ],
            "shapes": [
                {"name": shape.name, "image": shape.image.url}
                for shape in product.shapes.all()
            ],
            "files": [
                {"name": file.name, "file": file.file.url}
                for file in product.files.all()
            ],
        }

        # Test that we return a valid response on existing slug.
        with django_assert_max_num_queries(11):
            response = anonymous_client.get(
                f"{self.BASE_ENDPOINT}/product/{product.slug}/"
            )

            actual_response = json.loads(response.content)

            assert response.status_code == 200
            assert actual_response == expected_response

        # Test that we fail when an invalid slug is passed.
        with django_assert_max_num_queries(1):
            failed_response = anonymous_client.get(
                f"{self.BASE_ENDPOINT}/does-not-exist/"
            )

            assert failed_response.status_code == 404
