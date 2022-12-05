import json
from datetime import timedelta
from decimal import Decimal

from django.core.cache import cache
from django.utils import timezone

import pytest

from aria.discounts.tests.utils import create_discount
from aria.products.tests.utils import create_product, create_product_option

pytestmark = pytest.mark.django_db


class TestPublicDiscountsEndpoints:

    BASE_ENDPOINT = "/api/v1/discounts"

    def test_endpoint_discount_list_api(
        self, anonymous_client, django_assert_max_num_queries
    ) -> None:
        """
        Test retrieving active discounts from an anonymous client returns
        a valid response.
        """

        cache.clear()

        product_1 = create_product(product_name="Product 1")

        product_2 = create_product(product_name="Product 2")
        product_2_option_1 = create_product_option(product=product_2)

        product_3 = create_product(product_name="Product 3")
        product_4 = create_product(product_name="Product 4")

        discount_1 = create_discount(
            name="Discount 1 20%",
            products=[product_1, product_4],
            product_options=[product_2_option_1],
            discount_gross_percentage=Decimal("0.20"),
            active_at=timezone.now(),
            active_to=timezone.now() + timedelta(minutes=1),
            ordering=1,
        )
        discount_2 = create_discount(
            name="Discount 2 40%",
            products=[product_3],
            discount_gross_percentage=Decimal("0.40"),
            active_at=timezone.now(),
            active_to=timezone.now() + timedelta(minutes=1),
            ordering=2,
        )

        expected_response = [
            {
                "id": discount_1.id,
                "name": discount_1.name,
                "slug": discount_1.slug,
                "discountGrossPrice": None,
                "discountGrossPercentage": 0.2,
                "products": [
                    {
                        "id": product_4.id,
                        "name": product_4.name,
                        "slug": product_4.slug,
                        "unit": product_4.unit_display,
                        "supplier": {
                            "name": product_4.supplier.name,
                            "originCountry": product_4.supplier.country_name,
                            "originCountryFlag": product_4.supplier.unicode_flag,
                        },
                        "image380x575Url": product_4.image380x575_url,
                        "discount": {
                            "isDiscounted": True,
                            "discountedGrossPrice": 160.0,
                            "discountedGrossPercentage": 0.20,
                            "maximumSoldQuantity": None,
                            "remainingQuantity": None,
                        },
                        "displayPrice": True,
                        "fromPrice": 200.0,
                        "colors": [
                            {
                                "id": color.id,
                                "name": color.name,
                                "colorHex": color.color_hex,
                            }
                            for color in product_4.colors.all()
                        ],
                        "shapes": [
                            {
                                "id": shape.id,
                                "name": shape.name,
                                "imageUrl": shape.image.id,
                            }
                            for shape in product_4.shapes.all()
                        ],
                        "materials": product_4.materials_display,
                        "rooms": product_4.rooms_display,
                        "variants": [
                            {
                                "id": option.variant.id,
                                "name": option.variant.name,
                                "thumbnailUrl": option.variant.thumbnail.url
                                if option.variant.thumbnail
                                else None,
                                "imageUrl": option.variant.image.id
                                if option.variant.image
                                else None,
                            }
                            for option in product_4.options.all()
                            if option.variant
                        ],
                    },
                    {
                        "id": product_2_option_1.product.id,
                        "name": product_2_option_1.product.name,
                        "slug": product_2_option_1.product.slug,
                        "unit": product_2_option_1.product.unit_display,
                        "supplier": {
                            "name": product_2_option_1.product.supplier.name,
                            "originCountry": product_2_option_1.product.supplier.country_name,  # pylint: disable=line-too-long
                            "originCountryFlag": product_2_option_1.product.supplier.unicode_flag,  # pylint: disable=line-too-long
                        },
                        "image380x575Url": product_2.image380x575_url,
                        "discount": {
                            "isDiscounted": True,
                            "discountedGrossPrice": 160.0,
                            "discountedGrossPercentage": 0.20,
                            "maximumSoldQuantity": None,
                            "remainingQuantity": None,
                        },
                        "displayPrice": True,
                        "fromPrice": 200.0,
                        "colors": [
                            {
                                "id": color.id,
                                "name": color.name,
                                "color_hex": color.color_hex,
                            }
                            for color in product_2_option_1.product.colors.all()
                        ],
                        "shapes": [
                            {
                                "id": shape.id,
                                "name": shape.name,
                                "imageUrl": shape.image.id,
                            }
                            for shape in product_2_option_1.product.shapes.all()
                        ],
                        "materials": product_2_option_1.product.materials_display,
                        "rooms": product_2_option_1.product.rooms_display,
                        "variants": [
                            {
                                "id": option.variant.id,
                                "name": option.variant.name,
                                "thumbnailUrl": option.variant.thumbnail.url
                                if option.variant.thumbnail
                                else None,
                                "imageUrl": option.variant.image.id
                                if option.variant.image
                                else None,
                            }
                            for option in product_2_option_1.product.options.all()
                            if option.variant
                        ],
                    },
                    {
                        "id": product_1.id,
                        "name": product_1.name,
                        "slug": product_1.slug,
                        "unit": product_1.unit_display,
                        "supplier": {
                            "name": product_1.supplier.name,
                            "originCountry": product_1.supplier.country_name,
                            "originCountryFlag": product_1.supplier.unicode_flag,
                        },
                        "image380x575Url": product_1.image380x575_url,
                        "discount": {
                            "isDiscounted": True,
                            "discountedGrossPrice": 160.0,
                            "discountedGrossPercentage": 0.20,
                            "maximumSoldQuantity": None,
                            "remainingQuantity": None,
                        },
                        "displayPrice": True,
                        "fromPrice": 200.0,
                        "colors": [
                            {
                                "id": color.id,
                                "name": color.name,
                                "color_hex": color.color_hex,
                            }
                            for color in product_1.colors.all()
                        ],
                        "shapes": [
                            {
                                "id": shape.id,
                                "name": shape.name,
                                "imageUrl": shape.image.id,
                            }
                            for shape in product_1.shapes.all()
                        ],
                        "materials": product_1.materials_display,
                        "rooms": product_1.rooms_display,
                        "variants": [
                            {
                                "id": option.variant.id,
                                "name": option.variant.name,
                                "thumbnailUrl": option.variant.thumbnail.url
                                if option.variant.thumbnail
                                else None,
                                "imageUrl": option.variant.image.id
                                if option.variant.image
                                else None,
                            }
                            for option in product_1.options.all()
                            if option.variant
                        ],
                    },
                ],
            },
            {
                "id": discount_2.id,
                "name": discount_2.name,
                "slug": discount_2.slug,
                "discountGrossPrice": None,
                "discountGrossPercentage": 0.4,
                "products": [
                    {
                        "id": product_3.id,
                        "name": product_3.name,
                        "slug": product_3.slug,
                        "unit": product_3.unit_display,
                        "supplier": {
                            "name": product_3.supplier.name,
                            "originCountry": product_3.supplier.country_name,
                            "originCountryFlag": product_3.supplier.unicode_flag,
                        },
                        "image380x575Url": product_3.image380x575_url,
                        "discount": {
                            "isDiscounted": True,
                            "discountedGrossPrice": 120.0,
                            "discountedGrossPercentage": 0.40,
                            "maximumSoldQuantity": None,
                            "remainingQuantity": None,
                        },
                        "displayPrice": True,
                        "fromPrice": 200.0,
                        "colors": [
                            {
                                "id": color.id,
                                "name": color.name,
                                "color_hex": color.color_hex,
                            }
                            for color in product_3.colors.all()
                        ],
                        "shapes": [
                            {
                                "id": shape.id,
                                "name": shape.name,
                                "imageUrl": shape.image.id,
                            }
                            for shape in product_3.shapes.all()
                        ],
                        "materials": product_3.materials_display,
                        "rooms": product_3.rooms_display,
                        "variants": [
                            {
                                "id": option.variant.id,
                                "name": option.variant.name,
                                "thumbnailUrl": option.variant.thumbnail.url
                                if option.variant.thumbnail
                                else None,
                                "imageUrl": option.variant.image.id
                                if option.variant.image
                                else None,
                            }
                            for option in product_3.options.all()
                            if option.variant
                        ],
                    },
                ],
            },
        ]

        # Uses 10 queries.
        with django_assert_max_num_queries(10):
            response = anonymous_client.get(f"{self.BASE_ENDPOINT}/")

        actual_response = json.loads(response.content)

        assert response.status_code == 200
        assert actual_response == expected_response
