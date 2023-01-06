# pylint: disable=too-many-lines
import json
from datetime import timedelta
from decimal import Decimal
from unittest.mock import ANY

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test.client import MULTIPART_CONTENT
from django.utils import timezone

import pytest

from aria.categories.tests.utils import create_category
from aria.discounts.tests.utils import create_discount
from aria.product_attributes.models import Size
from aria.product_attributes.tests.utils import (
    create_color,
    create_material,
    create_room,
    create_shape,
    create_size,
    create_variant,
)
from aria.products.enums import ProductStatus, ProductUnit
from aria.products.models import Product
from aria.products.tests.utils import create_product, create_product_option
from aria.suppliers.tests.utils import get_or_create_supplier

pytestmark = pytest.mark.django_db


class TestPublicProductsEndpoints:

    BASE_ENDPOINT = "/api/v1/products"

    def test_endpoint_product_list_for_sale_api(
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
                        "image380x575Url": product.image380x575_url,
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
                                "imageUrl": shape.image.id,
                            }
                            for shape in product.shapes.all()
                        ],
                        "materials": [
                            {"id": material.id, "name": material.name}
                            for material in product.materials.all()
                        ],
                        "rooms": [
                            {"id": room.id, "name": room.name}
                            for room in product.rooms.all()
                        ],
                        "variants": [
                            {
                                "id": option.variant.id,
                                "name": option.variant.name,
                                "image80x80Url": option.variant.image80x80_url,
                                "image380x575Url": option.variant.image380x575_url,
                            }
                            for option in product.options.all()
                            if option.variant
                        ],
                    }
                    for product in products
                ]
            )
        )

        # Uses 9 queries:
        # - 1 for getting products,
        # - 1 for preloading colors,
        # - 1 for preloading materials,
        # - 1 for preloading rooms,
        # - 1 for preloading shapes,
        # - 1 for preloading options variants,
        # - 1 for preloading discounts
        # - 1 for preloading options,
        # - 1 for preloading discounts for options
        with django_assert_max_num_queries(9):
            response = anonymous_client.get(f"{self.BASE_ENDPOINT}/")

        actual_response = json.loads(response.content)

        assert response.status_code == 200
        assert len(actual_response) == 10
        assert actual_response == expected_response

    def test_endpoint_product_list_by_category_api(
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
                        "image380x575Url": product.image380x575_url,
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
                                "imageUrl": shape.image.id,
                            }
                            for shape in product.shapes.all()
                        ],
                        "materials": [
                            {"id": material.id, "name": material.name}
                            for material in product.materials.all()
                        ],
                        "rooms": [
                            {"id": room.id, "name": room.name}
                            for room in product.rooms.all()
                        ],
                        "variants": [
                            {
                                "id": option.variant.id,
                                "name": option.variant.name,
                                "image80x80Url": option.variant.image80x80_url,
                                "image380x575Url": option.variant.image380x575_url,
                            }
                            for option in product.options.all()
                            if option.variant
                        ],
                    }
                    for product in products
                ]
            )
        )

        # Uses 10 queries:
        # - 1 for resolving category
        # - 1 for getting products,
        # - 1 for preloading colors,
        # - 1 for preloading materials,
        # - 1 for preloading rooms,
        # - 1 for preloading shapes,
        # - 1 for preloading options variants,
        # - 1 for preloading discounts
        # - 1 for preloading discounts for options
        with django_assert_max_num_queries(10):
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

    def test_endpoint_product_detail_api(
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
                    "isMainImage": image.is_main_image,
                    "imageUrl": image.image_url,
                    "image1920x1080Url": image.image1920x1080_url,
                    "image1440x810Url": image.image1440x810_url,
                    "image1280x720Url": image.image1280x720_url,
                    "image1024x576Url": image.image1024x576_url,
                    "image960x540Url": image.image960x540_url,
                    "image768x432Url": image.image768x432_url,
                    "image640x360Url": image.image640x360_url,
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
                        "image80x80Url": None,
                        "image380x575Url": None,
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
                        "image80x80Url": None,
                        "image380x575Url": None,
                    },
                    "size": {
                        "id": option_2.size.id,
                        "name": option_2.size.name,
                    },
                },
            ],
            "materials": [
                {"id": material.id, "name": material.name}
                for material in product.materials.all()
            ],
            "rooms": [
                {"id": room.id, "name": room.name} for room in product.rooms.all()
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
        # Uses 14 queries:
        # - 1x for getting product
        # - 1x for prefetching category children
        # - 1x for prefetching categories
        # - 1x for prefetching colors
        # - 1x for prefetching materials
        # - 1x for prefetching rooms
        # - 1x for prefetching shapes
        # - 1x for prefetching files
        # - 1x for prefetching options
        # - 1x for prefetching options discounts
        # - 1x for prefetching product discounts
        # - 1x for filtering categories
        # - 1x for selecting related supplier
        # - 1x for prefetching images
        with django_assert_max_num_queries(14):
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

    #########################
    # Product list endpoint #
    #########################

    @pytest.mark.parametrize("test_permissions", ["product.view"], indirect=True)
    def test_endpoint_product_list_internal_api(
        self,
        anonymous_client,
        authenticated_unprivileged_client,
        authenticated_privileged_client,
        authenticated_unprivileged_staff_client,
        authenticated_privileged_staff_client,
        django_assert_max_num_queries,
        assert_client_response_is_status_code,
    ):
        """
        Test that privileged staff users gets a valid response on listing all products,
        and that all other request return appropriate HTTP status codes.
        """
        endpoint = f"{self.BASE_ENDPOINT}/"

        products = create_product(quantity=10)

        expected_response = {
            "next": None,
            "previous": None,
            "currentPage": 1,
            "total": 10,
            "currentRange": "1 - 10",
            "totalPages": 1,
            "data": [
                {
                    "id": product.id,
                    "name": product.name,
                    "slug": product.slug,
                    "status": product.status_display,
                    "supplier": {
                        "name": product.supplier.name,
                        "originCountry": product.supplier.country_name,
                        "originCountryFlag": product.supplier.unicode_flag,
                    },
                    "unit": product.unit_display,
                }
                for product in reversed(products)
            ],
        }

        # Anonymous users should get 401.
        assert_client_response_is_status_code(
            client=anonymous_client,
            endpoint=endpoint,
            max_allowed_queries=0,
            expected_status_code=401,
        )

        # Authenticated users without the correct permissions should get 401.
        assert_client_response_is_status_code(
            client=authenticated_unprivileged_client,
            endpoint=endpoint,
            max_allowed_queries=1,
            expected_status_code=401,
        )

        # Authenticated users with the correct permissions, but are not staff,
        # should get 401.
        assert_client_response_is_status_code(
            client=authenticated_privileged_client,
            endpoint=endpoint,
            max_allowed_queries=1,
            expected_status_code=401,
        )

        # Authenticated staff users without correct permissions should get 403.
        assert_client_response_is_status_code(
            client=authenticated_unprivileged_staff_client,
            endpoint=endpoint,
            max_allowed_queries=3,
            expected_status_code=403,
        )

        with django_assert_max_num_queries(12):
            response = authenticated_privileged_staff_client.get(endpoint)

        assert response.status_code == 200
        assert response.json() == expected_response

    ###########################
    # Product create endpoint #
    ###########################

    @pytest.mark.parametrize("test_permissions", ["product.management"], indirect=True)
    def test_endpoint_product_create_internal_api(  # pylint: disable=R0914
        self,
        anonymous_client,
        authenticated_unprivileged_client,
        authenticated_privileged_client,
        authenticated_unprivileged_staff_client,
        authenticated_privileged_staff_client,
        django_assert_max_num_queries,
        assert_client_response_is_status_code,
    ):
        """
        Test that privileged staff users gets a valid response on creating a new
        product, and that all other request return appropriate HTTP status codes.
        """

        endpoint = f"{self.BASE_ENDPOINT}/create/"

        supplier = get_or_create_supplier()
        main_category = create_category(name="Main")
        sub_category = create_category(name="Sub", parent=main_category)
        shape_square = create_shape(name="Square")
        color_white = create_color(name="White", color_hex="#FFFFFF")
        color_gray = create_color(name="Gray", color_hex="#CCCCCC")
        material_wood = create_material(name="Wood")
        material_steel = create_material(name="Steel")
        room_bathroom = create_room(name="Bathroom")

        products_in_db_count = Product.objects.count()

        # thumbnail = SimpleUploadedFile(
        #     "test.jpeg", b"data123", content_type="image/jpeg"
        # )

        payload = {
            "name": "New product",
            "status": ProductStatus.AVAILABLE,
            "slug": "new-product",
            "search_keywords": "keyword1",
            "description": "A new product!",
            "unit": 2,
            "vat_rate": 0.25,
            "available_in_special_sizes": False,
            "display_price": True,
            "can_be_purchased_online": True,
            "can_be_picked_up": True,
            "supplier_id": supplier.id,
            "category_ids": [sub_category.id],
            "material_ids": [material_wood.id, material_steel.id],
            "room_ids": [room_bathroom.id],
            "shape_ids": [shape_square.id],
            "color_ids": [color_white.id, color_gray.id],
            # "thumbnail": thumbnail,  # TODO: Replace when image migration is done.
        }

        expected_output = {
            "id": ANY,
            "name": "New product",
            "supplierId": supplier.id,
            "status": ProductStatus.AVAILABLE.label,
            "slug": "new-product",
            "description": "A new product!",
            "unit": ProductUnit.PCS.label,
            "vatRate": 0.25,
        }

        # Anonymous users should get 401.
        assert_client_response_is_status_code(
            client=anonymous_client,
            endpoint=endpoint,
            method="POST",
            max_allowed_queries=0,
            payload=payload,
            expected_status_code=401,
            content_type=MULTIPART_CONTENT,
        )

        # Authenticated users without the correct permissions should get 401.
        assert_client_response_is_status_code(
            client=authenticated_unprivileged_client,
            endpoint=endpoint,
            method="POST",
            max_allowed_queries=1,
            payload=payload,
            expected_status_code=401,
            content_type=MULTIPART_CONTENT,
        )

        # Authenticated users with the correct permissions, but are not staff,
        # should get 401.
        assert_client_response_is_status_code(
            client=authenticated_privileged_client,
            endpoint=endpoint,
            method="POST",
            max_allowed_queries=1,
            payload=payload,
            expected_status_code=401,
            content_type=MULTIPART_CONTENT,
        )

        # Authenticated staff users without correct permissions should get 403.
        assert_client_response_is_status_code(
            client=authenticated_unprivileged_staff_client,
            endpoint=endpoint,
            method="POST",
            max_allowed_queries=3,
            payload=payload,
            expected_status_code=403,
            content_type=MULTIPART_CONTENT,
        )

        with django_assert_max_num_queries(26):
            response = authenticated_privileged_staff_client.post(
                endpoint, data=payload
            )

        assert response.status_code == 201
        assert response.json() == expected_output
        assert Product.objects.count() == products_in_db_count + 1

        product = Product.objects.get(id=response.json()["id"])

        assert list(product.categories.all()) == [sub_category]
        assert list(product.shapes.all()) == [shape_square]
        assert list(product.colors.all()) == [color_white, color_gray]

        payload["supplier_id"] = 999

        with django_assert_max_num_queries(4):
            error_response = authenticated_privileged_staff_client.post(
                endpoint,
                data=payload,
                content_type=MULTIPART_CONTENT,
            )

        assert error_response.status_code == 404

    #################################
    # Product image create endpoint #
    #################################

    # Skip for now as image creating in the test using the SimpleUploadedFile utility
    # Causes issues with Pillow. Long term plan is to replace ImageKit and Pillow with
    # on-demand image CDN.
    @pytest.mark.skip
    @pytest.mark.parametrize("test_permissions", ["product.management"], indirect=True)
    def test_endpoint_product_image_create_internal_api(
        self,
        anonymous_client,
        authenticated_unprivileged_client,
        authenticated_privileged_client,
        authenticated_unprivileged_staff_client,
        authenticated_privileged_staff_client,
        django_assert_max_num_queries,
        assert_client_response_is_status_code,
    ):
        """
        Test that privileged staff users gets a valid response on creating a new
        product image, and that all other request return appropriate HTTP status codes.
        """

        product = create_product()

        assert product.images.count() == 0

        endpoint = f"{self.BASE_ENDPOINT}/{product.id}/images/create/"

        image = SimpleUploadedFile("test.jpeg", b"data123", content_type="image/jpeg")
        payload = {"apply_filter": False, "file": image}

        expected_response = {"id": ANY, "product_id": product.id, "image_url": ANY}

        # Anonymous users should get 401.
        assert_client_response_is_status_code(
            client=anonymous_client,
            endpoint=endpoint,
            method="POST",
            max_allowed_queries=0,
            payload=payload,
            expected_status_code=401,
            content_type=MULTIPART_CONTENT,
        )
        assert product.images.count() == 0

        # Authenticated users without the correct permissions should get 401.
        assert_client_response_is_status_code(
            client=authenticated_unprivileged_client,
            endpoint=endpoint,
            method="POST",
            max_allowed_queries=1,
            payload=payload,
            expected_status_code=401,
            content_type=MULTIPART_CONTENT,
        )
        assert product.images.count() == 0

        # Authenticated users with the correct permissions, but are not staff,
        # should get 401.
        assert_client_response_is_status_code(
            client=authenticated_privileged_client,
            endpoint=endpoint,
            method="POST",
            max_allowed_queries=1,
            payload=payload,
            expected_status_code=401,
            content_type=MULTIPART_CONTENT,
        )
        assert product.images.count() == 0

        # Authenticated staff users without correct permissions should get 403.
        assert_client_response_is_status_code(
            client=authenticated_unprivileged_staff_client,
            endpoint=endpoint,
            method="POST",
            max_allowed_queries=3,
            payload=payload,
            expected_status_code=403,
            content_type=MULTIPART_CONTENT,
        )
        assert product.images.count() == 0

        with django_assert_max_num_queries(0):
            response = authenticated_privileged_staff_client.post(
                endpoint, data=payload, content_type=MULTIPART_CONTENT
            )

        assert response.status_code == 201
        assert response.json() == expected_response

    ################################
    # Product file create endpoint #
    ################################

    @pytest.mark.parametrize("test_permissions", ["product.management"], indirect=True)
    def test_endpoint_product_file_create_internal_api(
        self,
        anonymous_client,
        authenticated_unprivileged_client,
        authenticated_privileged_client,
        authenticated_unprivileged_staff_client,
        authenticated_privileged_staff_client,
        django_assert_max_num_queries,
        assert_client_response_is_status_code,
    ):
        """
        Test that privileged staff users gets a valid response on creating a new
        product file, and that all other request return appropriate HTTP status codes.
        """

        product = create_product()

        assert product.files.count() == 0

        endpoint = f"{self.BASE_ENDPOINT}/{product.id}/files/create/"

        file = SimpleUploadedFile("test.pdf", b"data123")
        payload = {"name": "Catalog", "file": file}

        expected_response = {
            "id": ANY,
            "productId": product.id,
            "name": "Catalog",
            "file": ANY,
        }

        # Anonymous users should get 401.
        assert_client_response_is_status_code(
            client=anonymous_client,
            endpoint=endpoint,
            method="POST",
            max_allowed_queries=0,
            payload=payload,
            expected_status_code=401,
            content_type=MULTIPART_CONTENT,
        )
        assert product.files.count() == 0

        # Authenticated users without the correct permissions should get 401.
        assert_client_response_is_status_code(
            client=authenticated_unprivileged_client,
            endpoint=endpoint,
            method="POST",
            max_allowed_queries=1,
            payload=payload,
            expected_status_code=401,
            content_type=MULTIPART_CONTENT,
        )
        assert product.files.count() == 0

        # Authenticated users with the correct permissions, but are not staff,
        # should get 401.
        assert_client_response_is_status_code(
            client=authenticated_privileged_client,
            endpoint=endpoint,
            method="POST",
            max_allowed_queries=1,
            payload=payload,
            expected_status_code=401,
            content_type=MULTIPART_CONTENT,
        )
        assert product.files.count() == 0

        # Authenticated staff users without correct permissions should get 403.
        assert_client_response_is_status_code(
            client=authenticated_unprivileged_staff_client,
            endpoint=endpoint,
            method="POST",
            max_allowed_queries=3,
            payload=payload,
            expected_status_code=403,
            content_type=MULTIPART_CONTENT,
        )
        assert product.files.count() == 0

        # Uses 6 queries:
        # 3 - for checking user and permissions
        # 1 - for getting product
        # 1 - for getting supplier (for finding/creating correct folder)
        # 1 - for creating file
        with django_assert_max_num_queries(6):
            privileged_staff_response = authenticated_privileged_staff_client.post(
                endpoint, data=payload
            )

        assert privileged_staff_response.status_code == 201
        assert privileged_staff_response.json() == expected_response
        assert product.files.count() == 1
        assert product.files.first().name == "Catalog"
        assert product.files.first().file is not None

    ##################################
    # Product option create endpoint #
    ##################################

    @pytest.mark.parametrize("test_permissions", ["product.management"], indirect=True)
    def test_endpoint_product_option_create_internal_api(  # pylint: disable=too-many-locals, too-many-statements, line-too-long
        self,
        anonymous_client,
        authenticated_unprivileged_client,
        authenticated_privileged_client,
        authenticated_unprivileged_staff_client,
        authenticated_privileged_staff_client,
        django_assert_max_num_queries,
        assert_client_response_is_status_code,
    ):
        """
        Test that privileged staff users gets a valid response on creating a new
        product option and that all other request return appropriate HTTP status codes.
        """

        product = create_product()
        existing_size = create_size(
            width=Decimal("10.00"),
            height=Decimal("12.00"),
            depth=None,
            circumference=None,
        )
        existing_variant = create_variant(name="Test variant", is_standard=False)

        endpoint = f"{self.BASE_ENDPOINT}/{product.id}/options/create/"

        ###########
        # No size #
        ###########

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

        # Anonymous users should get 401.
        assert_client_response_is_status_code(
            client=anonymous_client,
            endpoint=endpoint,
            max_allowed_queries=0,
            method="POST",
            payload=no_size_payload,
            expected_status_code=401,
        )

        # Authenticated users without the correct permissions should get 401.
        assert_client_response_is_status_code(
            client=authenticated_unprivileged_client,
            endpoint=endpoint,
            max_allowed_queries=1,
            method="POST",
            payload=no_size_payload,
            expected_status_code=401,
        )

        # Authenticated users with the correct permissions, but are not staff,
        # should get 401.
        assert_client_response_is_status_code(
            client=authenticated_privileged_client,
            endpoint=endpoint,
            max_allowed_queries=1,
            method="POST",
            payload=no_size_payload,
            expected_status_code=401,
        )

        # Authenticated staff users without correct permissions should get 403.
        assert_client_response_is_status_code(
            client=authenticated_unprivileged_staff_client,
            endpoint=endpoint,
            max_allowed_queries=3,
            method="POST",
            payload=no_size_payload,
            expected_status_code=403,
        )

        with django_assert_max_num_queries(8):
            no_size_privileged_staff_response = (
                authenticated_privileged_staff_client.post(
                    endpoint,
                    data=no_size_payload,
                    content_type="application/json",
                )
            )

        assert no_size_privileged_staff_response.status_code == 201
        assert no_size_privileged_staff_response.json() == no_size_expected_response

        #################
        # Existing size #
        #################

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

        # Anonymous users should get 401.
        assert_client_response_is_status_code(
            client=anonymous_client,
            endpoint=endpoint,
            max_allowed_queries=0,
            method="POST",
            payload=existing_size_payload,
            expected_status_code=401,
        )

        # Authenticated users without the correct permissions should get 401.
        assert_client_response_is_status_code(
            client=authenticated_unprivileged_client,
            endpoint=endpoint,
            max_allowed_queries=1,
            method="POST",
            payload=existing_size_payload,
            expected_status_code=401,
        )

        # Authenticated users with the correct permissions, but are not staff,
        # should get 401.
        assert_client_response_is_status_code(
            client=authenticated_privileged_client,
            endpoint=endpoint,
            max_allowed_queries=1,
            method="POST",
            payload=existing_size_payload,
            expected_status_code=401,
        )

        # Authenticated staff users without correct permissions should get 403.
        assert_client_response_is_status_code(
            client=authenticated_unprivileged_staff_client,
            endpoint=endpoint,
            max_allowed_queries=3,
            method="POST",
            payload=existing_size_payload,
            expected_status_code=403,
        )

        with django_assert_max_num_queries(12):
            existing_size_privileged_staff_response = (
                authenticated_privileged_staff_client.post(
                    endpoint,
                    data=existing_size_payload,
                    content_type="application/json",
                )
            )

        assert existing_size_privileged_staff_response.status_code == 201
        assert (
            existing_size_privileged_staff_response.json()
            == existing_size_expected_response
        )

        ###############
        # Create size #
        ###############

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

        # Anonymous users should get 401.
        assert_client_response_is_status_code(
            client=anonymous_client,
            endpoint=endpoint,
            max_allowed_queries=0,
            method="POST",
            payload=create_size_payload,
            expected_status_code=401,
        )

        # Authenticated users without the correct permissions should get 401.
        assert_client_response_is_status_code(
            client=authenticated_unprivileged_client,
            endpoint=endpoint,
            max_allowed_queries=1,
            method="POST",
            payload=create_size_payload,
            expected_status_code=401,
        )

        # Authenticated users with the correct permissions, but are not staff,
        # should get 401.
        assert_client_response_is_status_code(
            client=authenticated_privileged_client,
            endpoint=endpoint,
            max_allowed_queries=1,
            method="POST",
            payload=create_size_payload,
            expected_status_code=401,
        )

        # Authenticated staff users without correct permissions should get 403.
        assert_client_response_is_status_code(
            client=authenticated_unprivileged_staff_client,
            endpoint=endpoint,
            max_allowed_queries=3,
            method="POST",
            payload=create_size_payload,
            expected_status_code=403,
        )

        with django_assert_max_num_queries(13):
            create_size_privileged_staff_response = (
                authenticated_privileged_staff_client.post(
                    endpoint,
                    data=create_size_payload,
                    content_type="application/json",
                )
            )

        assert create_size_privileged_staff_response.status_code == 201
        assert (
            create_size_privileged_staff_response.json()
            == create_size_expected_response
        )
        assert Size.objects.count() == sizes_in_db_count + 1

        #############################
        # No variant, existing size #
        #############################

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

        # Anonymous users should get 401.
        assert_client_response_is_status_code(
            client=anonymous_client,
            endpoint=endpoint,
            max_allowed_queries=0,
            method="POST",
            payload=no_variant_existing_size_payload,
            expected_status_code=401,
        )

        # Authenticated users without the correct permissions should get 401.
        assert_client_response_is_status_code(
            client=authenticated_unprivileged_client,
            endpoint=endpoint,
            max_allowed_queries=1,
            method="POST",
            payload=no_variant_existing_size_payload,
            expected_status_code=401,
        )

        # Authenticated users with the correct permissions, but are not staff,
        # should get 401.
        assert_client_response_is_status_code(
            client=authenticated_privileged_client,
            endpoint=endpoint,
            max_allowed_queries=1,
            method="POST",
            payload=no_variant_existing_size_payload,
            expected_status_code=401,
        )

        # Authenticated staff users without correct permissions should get 403.
        assert_client_response_is_status_code(
            client=authenticated_unprivileged_staff_client,
            endpoint=endpoint,
            max_allowed_queries=3,
            method="POST",
            payload=no_variant_existing_size_payload,
            expected_status_code=403,
        )

        with django_assert_max_num_queries(9):
            no_variant_existing_size_response = (
                authenticated_privileged_staff_client.post(
                    endpoint,
                    data=no_variant_existing_size_payload,
                    content_type="application/json",
                )
            )

        assert no_variant_existing_size_response.status_code == 201
        assert (
            no_variant_existing_size_response.json()
            == no_variant_existing_size_expected_response
        )

        ###########################
        # No variant, create size #
        ###########################

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

        # Anonymous users should get 401.
        assert_client_response_is_status_code(
            client=anonymous_client,
            endpoint=endpoint,
            max_allowed_queries=0,
            method="POST",
            payload=no_variant_create_size_payload,
            expected_status_code=401,
        )

        # Authenticated users without the correct permissions should get 401.
        assert_client_response_is_status_code(
            client=authenticated_unprivileged_client,
            endpoint=endpoint,
            max_allowed_queries=1,
            method="POST",
            payload=no_variant_create_size_payload,
            expected_status_code=401,
        )

        # Authenticated users with the correct permissions, but are not staff,
        # should get 401.
        assert_client_response_is_status_code(
            client=authenticated_privileged_client,
            endpoint=endpoint,
            max_allowed_queries=1,
            method="POST",
            payload=no_variant_create_size_payload,
            expected_status_code=401,
        )

        # Authenticated staff users without correct permissions should get 403.
        assert_client_response_is_status_code(
            client=authenticated_unprivileged_staff_client,
            endpoint=endpoint,
            max_allowed_queries=3,
            method="POST",
            payload=no_variant_create_size_payload,
            expected_status_code=403,
        )

        with django_assert_max_num_queries(10):
            no_variant_create_size_response = (
                authenticated_privileged_staff_client.post(
                    endpoint,
                    data=no_variant_create_size_payload,
                    content_type="application/json",
                )
            )

        assert no_variant_create_size_response.status_code == 201
        assert (
            no_variant_create_size_response.json()
            == no_variant_create_size_expected_response
        )
        assert Size.objects.count() == sizes_in_db_count + 1

        #######################
        # No variant, no size #
        #######################

        no_size_no_variant_payload = {
            "status": ProductStatus.AVAILABLE,
            "grossPrice": 999.50,
            "variantId": None,
            "size": None,
        }

        # Anonymous users should get 401.
        assert_client_response_is_status_code(
            client=anonymous_client,
            endpoint=endpoint,
            max_allowed_queries=0,
            method="POST",
            payload=no_size_no_variant_payload,
            expected_status_code=401,
        )

        # Authenticated users without the correct permissions should get 401.
        assert_client_response_is_status_code(
            client=authenticated_unprivileged_client,
            endpoint=endpoint,
            max_allowed_queries=1,
            method="POST",
            payload=no_size_no_variant_payload,
            expected_status_code=401,
        )

        # Authenticated users with the correct permissions, but are not staff,
        # should get 401.
        assert_client_response_is_status_code(
            client=authenticated_privileged_client,
            endpoint=endpoint,
            max_allowed_queries=1,
            method="POST",
            payload=no_size_no_variant_payload,
            expected_status_code=401,
        )

        # Authenticated staff users without correct permissions should get 403.
        assert_client_response_is_status_code(
            client=authenticated_unprivileged_staff_client,
            endpoint=endpoint,
            max_allowed_queries=3,
            method="POST",
            payload=no_size_no_variant_payload,
            expected_status_code=403,
        )

        with django_assert_max_num_queries(4):
            no_size_no_variant_response = authenticated_privileged_staff_client.post(
                endpoint,
                data=no_size_no_variant_payload,
                content_type="application/json",
            )

        assert no_size_no_variant_response.status_code == 400

    #######################################
    # Product option bulk create endpoint #
    #######################################

    @pytest.mark.parametrize("test_permissions", ["product.management"], indirect=True)
    def test_endpoint_product_option_bulk_create_internal_api(
        self,
        anonymous_client,
        authenticated_unprivileged_client,
        authenticated_privileged_client,
        authenticated_unprivileged_staff_client,
        authenticated_privileged_staff_client,
        django_assert_max_num_queries,
        assert_client_response_is_status_code,
    ):
        """
        Test that privileged staff users gets a valid response on creating new product
        options in bulk and that all other request return appropriate HTTP status codes.
        """

        product = create_product()
        variant = create_variant(name="Test variant")
        size = create_size(
            width=Decimal("20.0"),
            height=Decimal("10.0"),
            depth=Decimal("5.0"),
            circumference=None,
        )

        endpoint = f"{self.BASE_ENDPOINT}/{product.id}/options/bulk-create/"

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

        # Anonymous users should get 401.
        assert_client_response_is_status_code(
            client=anonymous_client,
            endpoint=endpoint,
            max_allowed_queries=0,
            method="POST",
            payload=payload,
            expected_status_code=401,
        )

        # Authenticated users without the correct permissions should get 401.
        assert_client_response_is_status_code(
            client=authenticated_unprivileged_client,
            endpoint=endpoint,
            max_allowed_queries=1,
            method="POST",
            payload=payload,
            expected_status_code=401,
        )

        # Authenticated users with the correct permissions, but are not staff,
        # should get 401.
        assert_client_response_is_status_code(
            client=authenticated_privileged_client,
            endpoint=endpoint,
            max_allowed_queries=1,
            method="POST",
            payload=payload,
            expected_status_code=401,
        )

        # Authenticated staff users without correct permissions should get 403.
        assert_client_response_is_status_code(
            client=authenticated_unprivileged_staff_client,
            endpoint=endpoint,
            max_allowed_queries=3,
            method="POST",
            payload=payload,
            expected_status_code=403,
        )

        with django_assert_max_num_queries(8):
            response = authenticated_privileged_staff_client.post(
                endpoint,
                data=payload,
                content_type="application/json",
            )

        assert response.status_code == 200
        assert response.json() == expected_response
        assert Size.objects.count() == sizes_in_db_count + 1
        assert product.options.count() == options_attached_to_product + 3
