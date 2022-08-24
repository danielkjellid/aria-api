import json
from datetime import timedelta
from decimal import Decimal

from django.utils import timezone

import pytest

from aria.categories.tests.utils import create_category
from aria.discounts.tests.utils import create_discount
from aria.products.enums import ProductStatus, ProductUnit
from aria.products.tests.utils import create_product, create_product_option

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

        create_discount(
            name="20% off",
            discount_gross_percentage=Decimal("0.20"),
            products=[products[0]],
            active_at=timezone.now(),
            active_to=timezone.now() + timedelta(minutes=5),
        )

        for product in products:
            product.categories.set([subcat_1])

        expected_response = list(
            reversed(
                [
                    {
                        "id": product.id,
                        "name": product.name,
                        "slug": product.slug,
                        "unit": ProductUnit(product.unit).label,
                        "supplier": {
                            "name": product.supplier.name,
                            "origin_country": product.supplier.origin_country.name,
                            "origin_country_flag": product.supplier.origin_country.unicode_flag,  # pylint: disable=line-too-long
                        },
                        "thumbnail": product.thumbnail.url
                        if product.thumbnail
                        else None,
                        "discount": {
                            "is_discounted": True,
                            "discounted_gross_price": 160.0,
                            "maximum_sold_quantity": None,
                            "remaining_quantity": None,
                        }
                        if product.discounts.exists()
                        else None,
                        "display_price": True,
                        "from_price": 200.0,
                        "colors": [
                            {
                                "id": color.id,
                                "name": color.name,
                                "color_hex": color.color_hex,
                            }
                            for color in product.colors.all()
                        ],
                        "shapes": [
                            {
                                "id": shape.id,
                                "name": shape.name,
                                "image": shape.image.id,
                            }
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
            )
        )

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

        product = create_product(options=[])
        option_1 = create_product_option(product=product, gross_price=Decimal("200.00"))
        option_2 = create_product_option(product=product, gross_price=Decimal("500.00"))

        create_discount(
            name="20% off",
            discount_gross_percentage=Decimal("0.20"),
            product_options=[option_1],
            active_at=timezone.now(),
            active_to=timezone.now() + timedelta(minutes=5),
        )

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
            "from_price": 200.0,
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
                    "id": option_1.id,
                    "gross_price": 200.0,
                    "discount": {
                        "is_discounted": True,
                        "discounted_gross_price": 160.0,
                        "maximum_sold_quantity": None,
                        "remaining_quantity": None,
                    },
                    "status": ProductStatus(option_1.status).label,
                    "variant": {
                        "id": option_1.variant.id,
                        "name": option_1.variant.name,
                        "image": None,
                        "thumbnail": None,
                    },
                    "size": {
                        "id": option_1.size.id,
                        "name": option_1.size.name,
                    },
                },
                {
                    "id": option_2.id,
                    "gross_price": 500.0,
                    "discount": None,
                    "status": ProductStatus(option_2.status).label,
                    "variant": {
                        "id": option_2.variant.id,
                        "name": option_2.variant.name,
                        "image": None,
                        "thumbnail": None,
                    },
                    "size": {
                        "id": option_2.size.id,
                        "name": option_2.size.name,
                    },
                },
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
        # Uses 12 queries:
        # - 1x for getting product
        # - 1x for prefetching category children
        # - 1x for prefetching categories
        # - 1x for prefetching colors
        # - 1x for prefetching shapes
        # - 1x for prefetching files
        # - 1x for prefetching options
        # - 1x for prefetching options discounts
        # - 1x for prefetching product discounts
        # - 1x for filtering categories
        # - 1x for selecting related supplier
        # - 1x for prefetching images
        with django_assert_max_num_queries(12):
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
