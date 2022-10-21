from decimal import Decimal

import pytest

from aria.products.models import Product
from aria.products.selectors.pricing import product_get_price_from_options
from aria.products.tests.utils import create_product, create_product_option

pytestmark = pytest.mark.django_db


class TestProductPricingSelectors:
    def test_selector_product_get_price_from_options(
        self, django_assert_max_num_queries
    ):
        """
        Test that the product_get_price_from_options selector returns
        the lowest product price based on options within query limits.
        """

        product = create_product()

        create_product_option(product=product, gross_price=Decimal("100.00"))
        create_product_option(product=product, gross_price=Decimal("200.00"))
        create_product_option(product=product, gross_price=Decimal("300.00"))
        create_product_option(product=product, gross_price=Decimal("400.00"))

        # Uses 1 query to aggregate price.
        with django_assert_max_num_queries(1):
            lowest_price = product_get_price_from_options(product=product)

        assert lowest_price == Decimal("100.00")

        product_with_annotation = (
            Product.objects.filter(id=product.id).annotate_from_price().first()
        )

        # Product with annotated value should not hit db.
        with django_assert_max_num_queries(0):
            lowest_annotated_price = product_get_price_from_options(
                product=product_with_annotation
            )

        assert lowest_annotated_price == Decimal("100.00")
