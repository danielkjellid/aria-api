import json
from datetime import timedelta
from decimal import Decimal
from unittest.mock import ANY

from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone

import pytest

from aria.categories.tests.utils import create_category
from aria.discounts.tests.utils import create_discount
from aria.products.enums import ProductStatus, ProductUnit
from aria.products.models import Size
from aria.products.tests.utils import (
    create_product,
    create_product_option,
    create_size,
    create_variant,
)

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

    BASE_ENDPOINT = "/api/v1/internal/products"

    ################################
    # Product file create endpoint #
    ################################

    def test_anonymous_request_product_file_create_internal_api(
        self, anonymous_client, django_assert_max_num_queries
    ):
        """
        Test that unauthenticated users gets a 401 unauthorized on creating a new
        product file.
        """

        product = create_product()

        assert product.files.all().count() == 0

        file = SimpleUploadedFile("test.pdf", b"data123")
        payload = {"name": "Catalog", "file": file}

        with django_assert_max_num_queries(0):
            response = anonymous_client.post(
                f"{self.BASE_ENDPOINT}/{product.id}/files/create/", data=payload
            )

        assert product.files.all().count() == 0
        assert response.status_code == 401

    def test_authenticated_unprivileged_request_product_file_create_internal_api(
        self, authenticated_unprivileged_client, django_assert_max_num_queries
    ):
        """
        Test that unauthenticated users gets a 403 forbidding on creating a new file.
        """

        product = create_product()

        assert product.files.all().count() == 0

        file = SimpleUploadedFile("test.pdf", b"data123")
        payload = {"name": "Catalog", "file": file}

        with django_assert_max_num_queries(3):
            response = authenticated_unprivileged_client.post(
                f"{self.BASE_ENDPOINT}/{product.id}/files/create/", data=payload
            )

        assert product.files.all().count() == 0
        assert response.status_code == 403

    @pytest.mark.parametrize("test_permissions", ["product.management"], indirect=True)
    def test_authenticated_privileged_request_variant_create_internal_api(
        self, authenticated_privileged_client, django_assert_max_num_queries
    ):
        """
        Test that privileged users gets a valid response on creating a new file.
        """

        product = create_product()

        assert product.files.all().count() == 0

        file = SimpleUploadedFile("test.pdf", b"data123")
        payload = {"name": "Catalog", "file": file}

        expected_response = {"productId": product.id, "name": "Catalog", "file": ANY}

        # Uses 6 queries:
        # 3 - for checking user and permissions
        # 1 - for getting product
        # 1 - for getting supplier (for finding/creating correct folder)
        # 1 - for creating file
        with django_assert_max_num_queries(6):
            response = authenticated_privileged_client.post(
                f"{self.BASE_ENDPOINT}/{product.id}/files/create/", data=payload
            )

        assert response.status_code == 201
        assert response.json() == expected_response
        assert product.files.all().count() == 1
        assert product.files.first().name == "Catalog"
        assert product.files.first().file is not None

    ##########################
    # Variants list endpoint #
    ##########################

    def test_anonymous_request_variant_list_internal_api(
        self, anonymous_client, django_assert_max_num_queries
    ):
        """
        Test that unauthenticated users gets a 401 unauthorized on listing
        all variants in the application.
        """

        with django_assert_max_num_queries(0):
            response = anonymous_client.get(f"{self.BASE_ENDPOINT}/variants/")

        assert response.status_code == 401

    def test_authenticated_unprivileged_request_variant_list_internal_api(
        self, authenticated_unprivileged_client, django_assert_max_num_queries
    ):
        """
        Test that unauthenticated users gets a 403 forbidding on listing
        all variants in the application.
        """

        with django_assert_max_num_queries(3):
            response = authenticated_unprivileged_client.get(
                f"{self.BASE_ENDPOINT}/variants/"
            )

        assert response.status_code == 403

    @pytest.mark.parametrize("test_permissions", ["product.management"], indirect=True)
    def test_authenticated_privileged_request_variant_list_internal_api(
        self,
        authenticated_privileged_client,
        django_assert_max_num_queries,
    ):
        """
        Test that privileged users gets a valid response on listing all variants in
        the application.
        """

        create_variant(name="Variant 1", is_standard=False)
        create_variant(name="Variant 2", is_standard=False)
        create_variant(name="Variant 3", is_standard=False)
        create_variant(name="Variant 4", is_standard=True)

        expected_response = [
            {
                "id": ANY,
                "name": "Variant 4",
                "isStandard": True,
                "image": None,
                "thumbnail": None,
            },
            {
                "id": ANY,
                "name": "Variant 3",
                "isStandard": False,
                "image": None,
                "thumbnail": None,
            },
            {
                "id": ANY,
                "name": "Variant 2",
                "isStandard": False,
                "image": None,
                "thumbnail": None,
            },
            {
                "id": ANY,
                "name": "Variant 1",
                "isStandard": False,
                "image": None,
                "thumbnail": None,
            },
        ]

        with django_assert_max_num_queries(4):
            response = authenticated_privileged_client.get(
                f"{self.BASE_ENDPOINT}/variants/"
            )

        actual_response = json.loads(response.content)

        assert response.status_code == 200
        assert len(actual_response) == 4
        assert actual_response == expected_response

    ############################
    # Variants create endpoint #
    ############################

    def test_anonymous_request_variant_create_internal_api(
        self, anonymous_client, django_assert_max_num_queries
    ):
        """
        Test that unauthenticated users gets a 401 unauthorized on creating a new
        variant.
        """

        file = SimpleUploadedFile("test.jpeg", b"data123")
        payload = {"name": "White mist", "is_standard": False, "file": file}

        with django_assert_max_num_queries(0):
            response = anonymous_client.post(
                f"{self.BASE_ENDPOINT}/variants/create/", data=payload
            )

        assert response.status_code == 401

    def test_authenticated_unprivileged_request_variant_create_internal_api(
        self, authenticated_unprivileged_client, django_assert_max_num_queries
    ):
        """
        Test that unauthenticated users gets a 403 forbidding on creating a new variant.
        """

        file = SimpleUploadedFile("test.jpeg", b"data123")
        payload = {"name": "White mist", "is_standard": False, "file": file}

        with django_assert_max_num_queries(3):
            response = authenticated_unprivileged_client.post(
                f"{self.BASE_ENDPOINT}/variants/create/", data=payload
            )

        assert response.status_code == 403

    # Skip for now as image creating in the test using the SimpleUploadedFile utility
    # Causes issues with Pillow. Long term plan is to replace ImageKit and Pillow with
    # on-demand image CDN.
    @pytest.mark.skip
    @pytest.mark.parametrize("test_permissions", ["product.management"], indirect=True)
    def test_authenticated_privileged_request_variant_create_internal_api(
        self, authenticated_privileged_client, django_assert_max_num_queries
    ):
        """
        Test that privileged users gets a valid response on creating a new variant.
        """

        file = SimpleUploadedFile("test.jpeg", b"data123")
        payload = {"name": "White mist", "is_standard": False, "file": file}

        expected_response = {
            "id": ANY,
            "name": "White mist",
            "isStandard": False,
            "image": None,
            "thumbnail": None,
        }

        with django_assert_max_num_queries(3):
            response = authenticated_privileged_client.post(
                f"{self.BASE_ENDPOINT}/variants/create/", data=payload
            )

        actual_response = json.loads(response.content)

        assert response.status_code == 201
        assert actual_response == expected_response

    ##################################
    # Product option create endpoint #
    ##################################

    def test_anonymous_request_product_option_create_internal_api(
        self, anonymous_client, django_assert_max_num_queries
    ):
        """
        Test that unauthenticated users gets a 401 unauthorized on creating a new
        product option.
        """

        product = create_product()
        payload = {
            "status": ProductStatus.AVAILABLE,
            "grossPrice": 99.00,
            "variantId": None,
            "size": {
                "width": 10.0,
                "height": 12.0,
                "depth": None,
                "circumference": None,
            },
        }

        with django_assert_max_num_queries(3):
            response = anonymous_client.post(
                f"{self.BASE_ENDPOINT}/{product.id}/options/create/",
                data=payload,
                content_type="application/json",
            )

        assert response.status_code == 401

    def test_authenticated_unprivileged_request_product_option_create_internal_api(
        self, authenticated_unprivileged_client, django_assert_max_num_queries
    ):
        """
        Test that unauthenticated users gets a 403 forbidding on creating a new product
        option.
        """

        product = create_product()
        payload = {
            "status": ProductStatus.AVAILABLE,
            "grossPrice": 99.00,
            "variantId": None,
            "size": {
                "width": 10.0,
                "height": 12.0,
                "depth": None,
                "circumference": None,
            },
        }

        with django_assert_max_num_queries(3):
            response = authenticated_unprivileged_client.post(
                f"{self.BASE_ENDPOINT}/{product.id}/options/create/",
                data=payload,
                content_type="application/json",
            )

        assert response.status_code == 403

    @pytest.mark.parametrize("test_permissions", ["product.management"], indirect=True)
    def test_authenticated_privileged_request_product_option_create_internal_api(
        self, authenticated_privileged_client, django_assert_max_num_queries
    ):

        product = create_product()
        existing_size = create_size(
            width=Decimal("10.00"),
            height=Decimal("12.00"),
            depth=None,
            circumference=None,
        )
        existing_variant = create_variant(name="Test variant", is_standard=False)

        no_size_payload = {
            "status": ProductStatus.AVAILABLE,
            "grossPrice": 101.49,
            "variantId": existing_variant.id,
        }
        no_size_expected_response = {
            "id": ANY,
            "status": ProductStatus.AVAILABLE,
            "grossPrice": 101.49,
            "sizeId": None,
            "variantId": existing_variant.id,
        }

        with django_assert_max_num_queries(8):
            no_size_response = authenticated_privileged_client.post(
                f"{self.BASE_ENDPOINT}/{product.id}/options/create/",
                data=no_size_payload,
                content_type="application/json",
            )

        assert no_size_response.status_code == 201
        assert no_size_response.json() == no_size_expected_response

        existing_size_payload = {
            "status": ProductStatus.AVAILABLE,
            "grossPrice": 102.00,
            "variantId": existing_variant.id,
            "size": {
                "width": 10.0,
                "height": 12.0,
                "depth": None,
                "circumference": None,
            },
        }
        existing_size_expected_response = {
            "id": ANY,
            "status": ProductStatus.AVAILABLE,
            "grossPrice": 102.00,
            "sizeId": existing_size.id,
            "variantId": existing_variant.id,
        }

        with django_assert_max_num_queries(12):
            existing_size_response = authenticated_privileged_client.post(
                f"{self.BASE_ENDPOINT}/{product.id}/options/create/",
                data=existing_size_payload,
                content_type="application/json",
            )

        assert existing_size_response.status_code == 201
        assert existing_size_response.json() == existing_size_expected_response

        sizes_in_db_count = Size.objects.count()

        create_size_payload = {
            "status": ProductStatus.AVAILABLE,
            "grossPrice": 50.00,
            "variantId": existing_variant.id,
            "size": {
                "width": 20.0,
                "height": 20.0,
                "depth": None,
                "circumference": None,
            },
        }
        create_size_expected_response = {
            "id": ANY,
            "status": ProductStatus.AVAILABLE,
            "grossPrice": 50.00,
            "variantId": existing_variant.id,
            "sizeId": ANY,
        }

        with django_assert_max_num_queries(13):
            create_size_response = authenticated_privileged_client.post(
                f"{self.BASE_ENDPOINT}/{product.id}/options/create/",
                data=create_size_payload,
                content_type="application/json",
            )

        assert create_size_response.status_code == 201
        assert create_size_response.json() == create_size_expected_response
        assert Size.objects.count() == sizes_in_db_count + 1

        no_variant_existing_size_payload = {
            "status": ProductStatus.AVAILABLE,
            "grossPrice": 500.50,
            "variantId": None,
            "size": {
                "width": 10.0,
                "height": 12.0,
                "depth": None,
                "circumference": None,
            },
        }
        no_variant_existing_size_expected_response = {
            "id": ANY,
            "status": ProductStatus.AVAILABLE,
            "grossPrice": 500.50,
            "variantId": None,
            "sizeId": ANY,
        }

        with django_assert_max_num_queries(9):
            no_variant_existing_size_response = authenticated_privileged_client.post(
                f"{self.BASE_ENDPOINT}/{product.id}/options/create/",
                data=no_variant_existing_size_payload,
                content_type="application/json",
            )

        assert no_variant_existing_size_response.status_code == 201
        assert (
            no_variant_existing_size_response.json()
            == no_variant_existing_size_expected_response
        )

        sizes_in_db_count = Size.objects.count()

        no_variant_create_size_payload = {
            "status": ProductStatus.AVAILABLE,
            "grossPrice": 349.50,
            "variantId": None,
            "size": {
                "width": 90.0,
                "height": 90.0,
                "depth": None,
                "circumference": None,
            },
        }
        no_variant_create_size_expected_response = {
            "id": ANY,
            "status": ProductStatus.AVAILABLE,
            "grossPrice": 349.50,
            "variantId": None,
            "sizeId": ANY,
        }

        with django_assert_max_num_queries(10):
            no_variant_create_size_response = authenticated_privileged_client.post(
                f"{self.BASE_ENDPOINT}/{product.id}/options/create/",
                data=no_variant_create_size_payload,
                content_type="application/json",
            )

        assert no_variant_create_size_response.status_code == 201
        assert (
            no_variant_create_size_response.json()
            == no_variant_create_size_expected_response
        )
        assert Size.objects.count() == sizes_in_db_count + 1

        no_size_no_variant_payload = {
            "status": ProductStatus.AVAILABLE,
            "grossPrice": 999.50,
            "variantId": None,
            "size": None,
        }

        with django_assert_max_num_queries(4):
            no_size_no_variant_response = authenticated_privileged_client.post(
                f"{self.BASE_ENDPOINT}/{product.id}/options/create/",
                data=no_size_no_variant_payload,
                content_type="application/json",
            )

        assert no_size_no_variant_response.status_code == 400

    #######################################
    # Product option bulk create endpoint #
    #######################################

    @pytest.mark.parametrize("test_permissions", ["product.management"], indirect=True)
    def test_authenticated_privileged_request_product_option_bulk_create_internal_api(
        self, authenticated_privileged_client, django_assert_max_num_queries
    ):

        product = create_product()
        variant = create_variant(name="Test variant")
        size = create_size(
            width=Decimal("20.0"),
            height=Decimal("10.0"),
            depth=Decimal("5.0"),
            circumference=None,
        )

        payload = [
            {
                "status": ProductStatus.AVAILABLE,
                "grossPrice": 500.0,
                "variantId": variant.id,
                "size": None,
            },
            {
                "status": ProductStatus.AVAILABLE,
                "grossPrice": 400.0,
                "variantId": None,
                "size": {
                    "width": None,
                    "height": None,
                    "depth": None,
                    "circumference": 30.0,
                },
            },
            {
                "status": ProductStatus.AVAILABLE,
                "grossPrice": 600.0,
                "variantId": variant.id,
                "size": {
                    "width": 20.0,
                    "height": 10.0,
                    "depth": 5.0,
                    "circumference": None,
                },
            },
        ]

        options_attached_to_product = product.options.count()
        sizes_in_db_count = Size.objects.count()

        assert options_attached_to_product == 1
        assert sizes_in_db_count == 2  # 1 created above, 1 created with product util.

        expected_response = [
            {
                "id": ANY,
                "status": ProductStatus.AVAILABLE,
                "grossPrice": 500.0,
                "variantId": variant.id,
                "sizeId": None,
            },
            {
                "id": ANY,
                "status": ProductStatus.AVAILABLE,
                "grossPrice": 400.0,
                "variantId": None,
                "sizeId": ANY,
            },
            {
                "id": ANY,
                "status": ProductStatus.AVAILABLE,
                "grossPrice": 600.0,
                "variantId": variant.id,
                "sizeId": size.id,
            },
        ]

        with django_assert_max_num_queries(6):
            response = authenticated_privileged_client.post(
                f"{self.BASE_ENDPOINT}/{product.id}/options/bulk-create/",
                data=payload,
                content_type="application/json",
            )

        assert response.status_code == 200
        assert response.json() == expected_response
        assert Size.objects.count() == sizes_in_db_count + 1
        assert product.options.count() == options_attached_to_product + 3

    #######################
    # Color list endpoint #
    #######################

    def test_anonymous_request_color_list_internal_api(
        self, anonymous_client, django_assert_max_num_queries
    ):
        assert False

    def test_authenticated_unprivileged_request_color_list_internal_api(
        self, authenticated_unprivileged_client, django_assert_max_num_queries
    ):
        assert False

    @pytest.mark.parametrize("test_permissions", ["product.management"], indirect=True)
    def test_authenticated_privileged_request_color_list_internal_api(
        self, authenticated_privileged_client, django_assert_max_num_queries
    ):
        assert False

    ########################
    # Shapes list endpoint #
    ########################

    def test_anonymous_request_shape_list_internal_api(
        self, anonymous_client, django_assert_max_num_queries
    ):
        assert False

    def test_authenticated_unprivileged_request_shape_list_internal_api(
        self, authenticated_unprivileged_client, django_assert_max_num_queries
    ):
        assert False

    @pytest.mark.parametrize("test_permissions", ["product.management"], indirect=True)
    def test_authenticated_privileged_request_shape_list_internal_api(
        self, authenticated_privileged_client, django_assert_max_num_queries
    ):
        assert False
