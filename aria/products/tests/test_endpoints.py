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

    BASE_ENDPOINT = "/api/v1/products"

    def test_anonymous_request_product_list_for_sale_api(
        self, anonymous_client, django_assert_max_num_queries
    ):
        """
        Test listing products for sale from an anonymous
        client returns a valid response.
        """

        products = create_product(quantity=10, status=ProductStatus.AVAILABLE)
        create_product(quantity=5, status=ProductStatus.DRAFT)

        expected_response = list(
            reversed(
                [
                    {
                        "id": product.id,
                        "name": product.name,
                        "slug": product.slug,
                        "unit": product.unit_display,
                        "supplier": {
                            "name": product.supplier.name,
                            "originCountry": product.supplier.country_name,
                            "originCountryFlag": product.supplier.unicode_flag,
                        },
                        "thumbnail": product.thumbnail.url
                        if product.thumbnail
                        else None,
                        "discount": None,
                        "displayPrice": True,
                        "fromPrice": 200.0,
                        "colors": [
                            {
                                "id": color.id,
                                "name": color.name,
                                "colorHex": color.color_hex,
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

        # Uses 7 queries:
        # - 1 for getting products,
        # - 1 for preloading colors,
        # - 1 for preloading shapes,
        # - 1 for preloading options variants,
        # - 1 for preloading discounts
        # - 1 for preloading options,
        # - 1 for preloading discounts for options
        with django_assert_max_num_queries(7):
            response = anonymous_client.get(f"{self.BASE_ENDPOINT}/")

        actual_response = json.loads(response.content)

        assert response.status_code == 200
        assert len(actual_response) == 10
        assert actual_response == expected_response

    def test_anonymous_request_product_list_by_category_api(
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
                            "originCountry": product.supplier.country_name,
                            "originCountryFlag": product.supplier.unicode_flag,
                        },
                        "thumbnail": product.thumbnail.url
                        if product.thumbnail
                        else None,
                        "discount": {
                            "isDiscounted": True,
                            "discountedGrossPrice": 160.0,
                            "discountedGrossPercentage": 0.20,
                            "maximumSoldQuantity": None,
                            "remainingQuantity": None,
                        }
                        if product.discounts.exists()
                        else None,
                        "displayPrice": True,
                        "fromPrice": 200.0,
                        "colors": [
                            {
                                "id": color.id,
                                "name": color.name,
                                "colorHex": color.color_hex,
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
        # - 1 for resolving category
        # - 1 for getting products,
        # - 1 for preloading colors,
        # - 1 for preloading shapes,
        # - 1 for preloading options variants,
        # - 1 for preloading discounts
        # - 1 for preloading options,
        # - 1 for preloading discounts for options
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
            "status": product.status_display,
            "unit": ProductUnit(product.unit).label,
            "name": product.name,
            "description": product.description,
            "absorption": product.absorption,
            "categories": [
                {
                    "name": "Furniture",
                    "parents": [{"name": "Parent", "parents": None, "slug": "parent"}],
                    "slug": "furniture",
                }
            ],
            "materials": product.materials_display,
            "rooms": product.rooms_display,
            "availableInSpecialSizes": product.available_in_special_sizes,
            "canBePickedUp": product.can_be_picked_up,
            "canBePurchasedOnline": product.can_be_purchased_online,
            "displayPrice": product.display_price,
            "fromPrice": 200.0,
            "supplier": {
                "name": product.supplier.name,
                "originCountry": product.supplier.country_name,
                "originCountryFlag": product.supplier.unicode_flag,
            },
            "images": [
                {
                    "applyFilter": image.apply_filter,
                    "image512x512": image.image_512x512.url,
                    "image640x275": image.image_640x275.url,
                    "image1024x575": image.image_1024x575.url,
                    "image1024x1024": image.image_1024x1024.url,
                    "image1536x860": image.image_1536x860.url,
                    "image2048x1150": image.image_2048x1150.url,
                }
                for image in product.images.all()
            ],
            "options": [
                {
                    "id": option_1.id,
                    "grossPrice": 200.0,
                    "discount": {
                        "isDiscounted": True,
                        "discountedGrossPrice": 160.0,
                        "discountedGrossPercentage": 0.20,
                        "maximumSoldQuantity": None,
                        "remainingQuantity": None,
                    },
                    "status": option_1.status_display,
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
                    "grossPrice": 500.0,
                    "discount": None,
                    "status": option_2.status_display,
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
                {"name": color.name, "colorHex": color.color_hex}
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
            response = anonymous_client.get(f"{self.BASE_ENDPOINT}/{product.slug}/")

            actual_response = json.loads(response.content)

            assert response.status_code == 200
            assert actual_response == expected_response

        # Test that we fail when an invalid slug is passed.
        with django_assert_max_num_queries(1):
            failed_response = anonymous_client.get(
                f"{self.BASE_ENDPOINT}/does-not-exist/"
            )

            assert failed_response.status_code == 400


class TestInternalProductsEndpoints:

    BASE_ENDPOINT = "/api/v1/products/internal/"

    def test_anonymous_request_variant_list_internal_api(
        self, anonymous_client, django_assert_max_num_queries
    ):
        assert False

    def test_anonymous_request_variant_create_internal_api(
        self, anonymous_client, django_assert_max_num_queries
    ):
        assert False
