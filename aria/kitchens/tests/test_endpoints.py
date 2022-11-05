import json

import pytest

from aria.kitchens.tests.utils import create_kitchen
from aria.products.enums import ProductStatus

pytestmark = pytest.mark.django_db


class TestPublicKitchensEndpoints:

    BASE_ENDPOINT = "/api/v1/kitchens"

    def test_anonymous_request_kitchen_list_api(
        self, anonymous_client, django_assert_max_num_queries
    ) -> None:
        """
        Test retrieving a list of available kitchens from an anonymous client returns
        a valid response.
        """

        available_kitchen_1 = create_kitchen(name="Kitchen 1")
        available_kitchen_2 = create_kitchen(name="Kitchen 2")
        available_kitchen_3 = create_kitchen(name="Kitchen 3")

        # Create a kitchen with unavailable status as well, to
        # test if it's filtered out.
        create_kitchen(name="Kitchen 4", status=ProductStatus.DRAFT)

        expected_response = [
            {
                "id": available_kitchen_3.id,
                "name": available_kitchen_3.name,
                "slug": available_kitchen_3.slug,
                "thumbnailDescription": available_kitchen_3.thumbnail_description,
                "listImages": {
                    "imageUrl": available_kitchen_3.image_url,
                    "image960x540Url": available_kitchen_3.image960x540_url,
                    "image576x324Url": available_kitchen_3.image576x324_url,
                },
            },
            {
                "id": available_kitchen_2.id,
                "name": available_kitchen_2.name,
                "slug": available_kitchen_2.slug,
                "thumbnailDescription": available_kitchen_2.thumbnail_description,
                "listImages": {
                    "imageUrl": available_kitchen_2.image_url,
                    "image960x540Url": available_kitchen_2.image960x540_url,
                    "image576x324Url": available_kitchen_2.image576x324_url,
                },
            },
            {
                "id": available_kitchen_1.id,
                "name": available_kitchen_1.name,
                "slug": available_kitchen_1.slug,
                "thumbnailDescription": available_kitchen_1.thumbnail_description,
                "listImages": {
                    "imageUrl": available_kitchen_1.image_url,
                    "image960x540Url": available_kitchen_1.image960x540_url,
                    "image576x324Url": available_kitchen_1.image576x324_url,
                },
            },
        ]

        # Uses 1 query to get kitchens.
        with django_assert_max_num_queries(1):
            response = anonymous_client.get(f"{self.BASE_ENDPOINT}/")

        actual_response = json.loads(response.content)

        assert response.status_code == 200
        assert actual_response == expected_response

    def test_anonymous_request_kitchen_detail_api(
        self, anonymous_client, django_assert_max_num_queries
    ) -> None:
        """
        Test retrieving a single kitchen from an anonymous client returns
        a valid response.
        """

        kitchen = create_kitchen()

        expected_response = {
            "id": kitchen.id,
            "name": kitchen.name,
            "slug": kitchen.slug,
            "description": kitchen.description,
            "extraDescription": kitchen.extra_description,
            "exampleFromPrice": "40000.00",
            "canBePainted": kitchen.can_be_painted,
            "silkVariants": [
                {"name": obj.name, "colorHex": obj.color_hex}
                for obj in kitchen.silk_variants.all()
            ],
            "decorVariants": [
                {"name": obj.name, "image": obj.image.url}
                for obj in kitchen.decor_variants.all()
            ],
            "plywoodVariants": [
                {"name": obj.name, "image": obj.image.url}
                for obj in kitchen.plywood_variants.all()
            ],
            "laminateVariants": [
                {"name": obj.name, "color_hex": obj.color_hex}
                for obj in kitchen.laminate_variants.all()
            ],
            "exclusiveVariants": [
                {"name": obj.name, "color_hex": obj.color_hex}
                for obj in kitchen.exclusive_variants.all()
            ],
            "trendVariants": [
                {"name": obj.name, "color_hex": obj.color_hex}
                for obj in kitchen.trend_variants.all()
            ],
            "images": {
                "applyFilter": kitchen.apply_filter,
                "isMainImage": kitchen.is_main_image,
                "imageUrl": kitchen.image_url,
                "image1440x810Url": kitchen.image1440x810_url,
                "image1280x720Url": kitchen.image1280x720_url,
                "image1024x576Url": kitchen.image1024x576_url,
                "image960x540Url": kitchen.image960x540_url,
                "image768x432Url": kitchen.image768x432_url,
                "image640x360Url": kitchen.image640x360_url,
            },
        }

        # Uses 7 queries:
        # - 1 for getting kitchen + supplier
        # - 6 for prefetching related objects.
        with django_assert_max_num_queries(7):
            response = anonymous_client.get(f"{self.BASE_ENDPOINT}/{kitchen.slug}/")

        actual_response = json.loads(response.content)

        assert response.status_code == 200
        assert actual_response == expected_response

        # Test that we fail when an invalid slug is passed.
        with django_assert_max_num_queries(1):
            failed_response = anonymous_client.get(
                f"{self.BASE_ENDPOINT}/does-not-exist/"
            )

        assert failed_response.status_code == 400
