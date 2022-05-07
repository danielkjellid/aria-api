import json
import tempfile

import pytest
from model_bakery import baker

from aria.categories.models import Category
from aria.categories.viewsets.public import (
    CategoryChildrenListAPI,
    CategoryDetailAPI,
    CategoryListAPI,
    CategoryParentListAPI,
    CategoryProductsListAPI,
)
from aria.products.models import Product


class TestPublicCategoriesSerializers:
    #####################
    # Input serializers #
    #####################

    # Currently none

    ######################
    # Output serializers #
    ######################

    @pytest.mark.django_db
    def test_output_serializer_category_list(self):
        """
        Test output serializer validity of the ProductDetailAPI endpoint.
        """

        category_1, category_2 = baker.make(Category, _quantity=2)
        subcategory_1 = baker.make(Category, **{"parent": category_1})
        subcategory_2 = baker.make(Category, **{"parent": category_2})

        expected_output = [
            {
                "id": category_1.id,
                "name": category_1.name,
                "slug": category_1.slug,
                "ordering": category_1.ordering,
                "children": [
                    {
                        "id": subcategory_1.id,
                        "name": subcategory_1.name,
                        "slug": subcategory_1.slug,
                        "ordering": subcategory_1.ordering,
                    }
                ],
            },
            {
                "id": category_2.id,
                "name": category_2.name,
                "slug": category_2.slug,
                "ordering": category_2.ordering,
                "children": [
                    {
                        "id": subcategory_2.id,
                        "name": subcategory_2.name,
                        "slug": subcategory_2.slug,
                        "ordering": subcategory_2.ordering,
                    }
                ],
            },
        ]

        serializer = CategoryListAPI.OutputSerializer(
            [category_1, category_2], many=True
        )

        assert serializer.data
        assert serializer.data == expected_output

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
