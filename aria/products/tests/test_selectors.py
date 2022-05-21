import pytest
from aria.products.selectors import (
    product_list_by_category,
    product_options_list_for_product,
    product_detail,
)
from aria.products.models import Product
from aria.products.tests.utils import create_product, create_product_option
from aria.categories.tests.utils import create_category
from decimal import Decimal

pytestmark = pytest.mark.django_db


class TestProductsSelectors:
    def test_product_list_by_category(self, django_assert_max_num_queries):
        """
        Test that the product_list_by_category is able to get products
        with right category, and filter's the query correctly if needed.
        """

        category_1 = create_category()
        subcategory_1 = create_category(name="Floor times", parent=category_1)
        products_cat_1 = create_product(quantity=5)

        # Set all categories in products_cat_1 to subcategory_1.
        for product in products_cat_1:
            product.categories.set([subcategory_1])

        category_2 = create_category()
        subcategory_2 = create_category(name="Wall tiles", parent=category_2)
        products_cat_2 = create_product(quantity=3)

        # Set all categories in products_cat_1 to subcategory_1.
        for product in products_cat_2:
            product.categories.set([subcategory_2])

        # Manually set atributes to be able to filter later on.
        products_cat_2[0].name = "Awesome product"
        products_cat_2[0].save()
        products_cat_2[1].materials = ["wood"]
        products_cat_2[1].save()

        # Check that we're in a good place before continuing.
        assert Product.objects.count() == 8

        # Test initially filtering on subcategory_1.
        with django_assert_max_num_queries(7):
            filtered_product_subcat_1 = product_list_by_category(
                filters=None, category=subcategory_1
            )

        # Assert that it's only the 5 connected to the query thats returned.
        assert len(filtered_product_subcat_1) == 5

        # Test filtering on subcategory_2.
        with django_assert_max_num_queries(7):
            filtered_product_subcat_2 = product_list_by_category(
                filters=None, category=subcategory_2
            )

        # Assert that it's only the 3 connected to the query thats returned.
        assert len(filtered_product_subcat_2) == 3

        # Test filtering on subcategory_2 and name = "Awesome product".
        with django_assert_max_num_queries(7):
            filtered_product_subcat_2 = product_list_by_category(
                filters={"search": "Awesome product"}, category=subcategory_2
            )

        # Assert that only one item is returned, and the item in question
        # is the first element in products_cat_2.
        assert len(filtered_product_subcat_2) == 1
        assert filtered_product_subcat_2[0].id == products_cat_2[0].id

        # Test filtering on subcategory_2 and partial material "woo".
        with django_assert_max_num_queries(7):
            filtered_product_subcat_2 = product_list_by_category(
                filters={"search": "woo"}, category=subcategory_2
            )

        # Assert that only one item is returned, and the item in question
        # is the second element in products_cat_2.
        assert len(filtered_product_subcat_2) == 1
        assert filtered_product_subcat_2[0].id == products_cat_2[1].id

    def test_product_options_list_for_product(self, django_assert_max_num_queries):
        """
        Test that the product_options_list_for_product selector returns
        as expected, both with and without a prefetch.
        """

        product_1 = create_product(product_name="Product 1")
        create_product_option(product=product_1)
        create_product_option(product=product_1, gross_price=Decimal(300.00))
        create_product_option(product=product_1, gross_price=Decimal(400.00))

        # First test without prefetched attribute.
        # Uses 1 query for getting options + sizes.
        with django_assert_max_num_queries(1):
            options = product_options_list_for_product(product=product_1)

        assert len(options) == 3

        # Prefetching here uses 2 queries, but we usually have to get
        # the product somehow anyways.
        prefetched_product = (
            Product.objects.filter(id=product_1.id).with_available_options().first()
        )

        # Test with prefetched attribute.
        # Uses 0 queries if the arg sent in is already prefetched.
        with django_assert_max_num_queries(0):
            options = product_options_list_for_product(product=prefetched_product)

        assert len(options) == 3

    def test_product_detail(self, django_assert_max_num_queries):
        """
        Test that the product_detail selector works as expected and does
        not use an obscene amount of queries. It's a big boy.
        """

        product = create_product()

        # Uses 12 queries: Uses 7 to get basic product details and relations,
        # 4 to get right amount og categories and 1 to get options.
        with django_assert_max_num_queries(12):
            fetched_product = product_detail(product_id=product.id)

        assert fetched_product.id == product.id
        assert len(fetched_product.options) == len(product.options.all())
        assert len(fetched_product.categories) == len(product.categories.all())
        assert len(fetched_product.images) == len(product.images.all())
        assert len(fetched_product.shapes) == len(product.shapes.all())
        assert len(fetched_product.colors) == len(product.colors.all())
