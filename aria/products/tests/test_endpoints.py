import json

import pytest

from aria.products.enums import ProductStatus, ProductUnit
from aria.products.tests.utils import create_product

pytestmark = pytest.mark.django_db


class TestPublicProductsEndpoints:

    BASE_ENDPOINT = "/api/products"

    def test_anonymous_request_product_detail_api(
        self, anonymous_client, django_assert_max_num_queries
    ):
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
            "description": product.description,
            "absorption": product.absorption,
            "materials": product.materials_display,
            "rooms": product.rooms_display,
            "available_in_special_sizes": product.available_in_special_sizes,
            "supplier": {
                "name": product.supplier.name,
                "origin_country": product.supplier.origin_country,
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
                    }
                    if option.variant
                    else None,
                    "size": {
                        "id": option.size.id,
                        "width": option.size.width,
                        "height": option.size.height,
                        "depth": option.size.depth,
                        "circumference": option.size.circumference,
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

            assert failed_response.status_code == 404
