from decimal import Decimal

import pytest

from aria.products.models import Product
from aria.products.selectors import product_detail, product_options_list_for_product
from aria.products.tests.utils import create_product, create_product_option

pytestmark = pytest.mark.django_db


class TestProductsSelectors:
    def test_product_options_list_for_product(
        self, django_assert_max_num_queries
    ) -> None:
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

    def test_product_detail(self, django_assert_max_num_queries) -> None:
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
