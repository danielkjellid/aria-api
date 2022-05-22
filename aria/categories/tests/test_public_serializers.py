import json
import tempfile

import pytest
from model_bakery import baker

from aria.categories.models import Category
from aria.categories.viewsets.public import CategoryProductsListAPI
from aria.products.models import Product


class TestPublicCategoriesSerializers:
    @pytest.mark.django_db
    def test_output_serializer_category_products_list(self):
        """
        Test output serializer validity of the ProductDetailAPI endpoint.
        """

        category = baker.make(Category)
        subcategory = baker.make(Category, **{"parent": category})
        products = baker.make(Product, _quantity=5)

        for product in products:
            product.categories.add(subcategory)
            product.thumbnail = tempfile.NamedTemporaryFile(suffix=".jpg").name
            product.save()

        expected_output = [
            {
                "id": product.id,
                "name": product.name,
                "slug": product.slug,
                "unit": product.get_unit_display(),
                "thumbnail": product.thumbnail.url,
                "display_price": product.get_display_price(),
                "from_price": product.get_lowest_option_price(),
                "colors": [],
                "shapes": [],
                "materials": [],
                "variants": [],
            }
            for product in products
        ]

        serializer = CategoryProductsListAPI.OutputSerializer(products, many=True)

        assert serializer.data
        assert json.dumps(serializer.data) == json.dumps(expected_output)
