from decimal import Decimal

import pytest

from aria.products.models import Product
from aria.products.selectors.options import product_options_list_for_product
from aria.products.tests.utils import create_product, create_product_option

pytestmark = pytest.mark.django_db


class TestProductOptionsSelectors:
    def test_selector_product_options_list_for_product(
        self, django_assert_max_num_queries
    ) -> None:
        """
        Test that the product_options_list_for_product selector returns
        as expected, both with and without a prefetch.
        """

        product_1 = create_product(product_name="Test Product 1", options=[])
        create_product_option(product=product_1)
        create_product_option(product=product_1, gross_price=Decimal(300.00))
        create_product_option(product=product_1, gross_price=Decimal(400.00))

        # First test without prefetched attribute.
        # Uses 1 query for getting options + sizes and 1 for prefetching
        # active discounts.
        with django_assert_max_num_queries(2):
            options = product_options_list_for_product(product=product_1)

        assert len(options) == 3

        prefetched_product = (
            Product.objects.filter(id=product_1.id)
            .with_available_options_and_option_discounts()
            .first()
        )

        # Test with prefetched attribute.
        # Uses 0 queries if the arg sent in is already prefetched.
        with django_assert_max_num_queries(0):
            options = product_options_list_for_product(product=prefetched_product)

        assert len(options) == 3
