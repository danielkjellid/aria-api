import json
import tempfile

import pytest
from model_bakery import baker

from aria.categories.models import Category
from aria.categories.viewsets.public import (
    CategoryChildrenListAPI,
    CategoryDetailAPI,
    CategoryParentListAPI,
    CategoryProductsListAPI,
)
from aria.products.models import Product


class TestPublicCategoriesSerializers:
    @pytest.mark.django_db
    def test_output_serializer_category_detail(self):
        """
        Test output serializer validity of the ProductDetailAPI endpoint.
        """

        category = baker.make(Category)

        expected_output = {
            "id": category.id,
            "name": category.name,
            "slug": category.slug,
            "images": {
                "apply_filter": category.apply_filter,
                "image_1024x1024": category.image_1024x1024.url,
                "image_1024x575": category.image_1024x575.url,
                "image_1536x860": category.image_1536x860.url,
                "image_2048x1150": category.image_2048x1150.url,
                "image_512x512": category.image_512x512.url,
                "image_640x275": category.image_640x275.url,
            },
        }

        serializer = CategoryDetailAPI.OutputSerializer(category)

        assert serializer.data
        assert serializer.data == expected_output

    @pytest.mark.django_db
    def test_output_serializer_category_parent_list(self):
        """
        Test output serializer validity of the ProductDetailAPI endpoint.
        """

        category = baker.make(Category)

        expected_output = {
            "id": category.id,
            "name": category.name,
            "slug": category.slug,
            "ordering": category.ordering,
            "images": {
                "apply_filter": category.apply_filter,
                "image_1024x1024": category.image_1024x1024.url,
                "image_1024x575": category.image_1024x575.url,
                "image_1536x860": category.image_1536x860.url,
                "image_2048x1150": category.image_2048x1150.url,
                "image_512x512": category.image_512x512.url,
                "image_640x275": category.image_640x275.url,
            },
        }

        serializer = CategoryParentListAPI.OutputSerializer(category)

        assert serializer.data
        assert serializer.data == expected_output

    @pytest.mark.django_db
    def test_output_serializer_category_parent_children_list(self):
        """
        Test output serializer validity of the ProductDetailAPI endpoint.
        """

        children = baker.make(Category, _quantity=5)

        expected_output = [
            {
                "id": child.id,
                "name": child.name,
                "slug": child.slug,
                "ordering": child.ordering,
                "description": child.description,
                "images": {
                    "image500x305": child.image500x305.url,
                    "image600x440": child.image600x440.url,
                    "image850x520": child.image850x520.url,
                },
            }
            for child in children
        ]

        serializer = CategoryChildrenListAPI.OutputSerializer(children, many=True)

        assert serializer.data
        assert serializer.data == expected_output

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
