import pytest
from model_bakery import baker

from aria.products.models import Product
from aria.products.viewsets.public import ProductDetailAPI


class TestPublicProductsSerializers:
    #####################
    # Input serializers #
    #####################

    # Currently none

    ######################
    # Output serializers #
    ######################

    @pytest.mark.django_db
    def test_output_serializer_products_detail(self):
        """
        Test output serializer validity of the ProductDetailAPI endpoint.
        """

        product = baker.make(Product)

        expected_output = {
            "id": product.id,
            "status": product.get_status_display(),
            "unit": product.get_unit_display(),
            "name": product.name,
            "description": product.new_description,  # TODO: change to just description after we have migrated over.
            "images": [],
            "absorption": product.absorption,
            "materials": product.get_materials_display(),
            "rooms": product.get_rooms_display(),
            "supplier": product.supplier.name,
            "origin_country": product.supplier.origin_country,
            "available_in_special_sizes": product.available_in_special_sizes,
            "options": [],
            "colors": [],
            "shapes": [],
            "files": [],
        }

        serializer = ProductDetailAPI.OutputSerializer(product)

        assert serializer.data
        assert serializer.data == expected_output
