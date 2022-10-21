from datetime import timedelta
from decimal import Decimal

from django.utils import timezone

import pytest

from aria.discounts.tests.utils import create_discount
from aria.products.models import Product, ProductOption
from aria.products.selectors.discounts import (
    _calculate_discounted_price,
    product_calculate_discounted_price,
    product_get_active_discount,
    product_option_calculate_discounted_price,
    product_option_get_active_discount,
)
from aria.products.tests.utils import create_product, create_product_option

pytestmark = pytest.mark.django_db


class TestProductDiscountsSelectors:
    def test_selector__calculate_discounted_price(
        self, django_assert_max_num_queries
    ) -> None:
        """
        Test that the _calculate_discounted_price selector calculates and
        returns correct value within query limits.
        """

        percentage_discount = create_discount(
            discount_gross_percentage=Decimal("0.20"),
            active_at=timezone.now(),
            active_to=timezone.now() + timedelta(minutes=10),
        )

        fixed_price_discount = create_discount(
            discount_gross_price=Decimal("200.00"),
            active_at=timezone.now(),
            active_to=timezone.now() + timedelta(minutes=10),
        )

        with django_assert_max_num_queries(0):
            discounted_percentage_price = _calculate_discounted_price(
                price=Decimal("100.00"), discount=percentage_discount
            )

        with django_assert_max_num_queries(0):
            discounted_fixed_price = _calculate_discounted_price(
                price=Decimal("400.00"), discount=fixed_price_discount
            )

        assert discounted_percentage_price == Decimal("80.00")
        assert discounted_fixed_price == Decimal("200.00")

    def test_selector_product_calculate_discounted_price(
        self, django_assert_max_num_queries
    ):
        """
        Test that the product_calculate_discounted_price selector
        calculates and returns correct value within query limits.
        """

        product_1 = create_product(product_name="Product 1")
        create_product_option(product=product_1, gross_price=Decimal("100.00"))
        product_1 = Product.objects.filter(id=product_1.id).preload_for_list().first()

        percentage_discount = create_discount(
            discount_gross_percentage=Decimal("0.20"),
            products=[product_1],
            active_at=timezone.now(),
            active_to=timezone.now() + timedelta(minutes=10),
        )

        product_2 = create_product(product_name="Product 2")
        create_product_option(product=product_2, gross_price=Decimal("500.00"))
        product_2 = Product.objects.filter(id=product_2.id).preload_for_list().first()

        fixed_price_discount = create_discount(
            discount_gross_price=Decimal("200.00"),
            products=[product_2],
            active_at=timezone.now(),
            active_to=timezone.now() + timedelta(minutes=10),
        )

        with django_assert_max_num_queries(0):
            discounted_percentage_price = product_calculate_discounted_price(
                product=product_1, discount=percentage_discount
            )

        with django_assert_max_num_queries(0):
            discounted_fixed_price = product_calculate_discounted_price(
                product=product_2, discount=fixed_price_discount
            )

        assert discounted_percentage_price == Decimal("80.00")
        assert discounted_fixed_price == Decimal("200.00")

    def test_selector_product_option_calculate_discounted_price(
        self, django_assert_max_num_queries
    ):
        """
        Test that the product_option_calculate_discounted_price selector
        calculates and returns correct value within query limits.
        """

        option_1 = create_product_option(
            product=create_product(product_name="Product 1"),
            gross_price=Decimal("100.00"),
        )
        option_2 = create_product_option(
            product=create_product(product_name="Product 2"),
            gross_price=Decimal("500.00"),
        )

        percentage_discount = create_discount(
            discount_gross_percentage=Decimal("0.30"),
            active_at=timezone.now(),
            active_to=timezone.now() + timedelta(minutes=10),
        )

        fixed_price_discount = create_discount(
            discount_gross_price=Decimal("100.00"),
            active_at=timezone.now(),
            active_to=timezone.now() + timedelta(minutes=10),
        )

        with django_assert_max_num_queries(0):
            discounted_percentage_price = product_option_calculate_discounted_price(
                option=option_1, discount=percentage_discount
            )

        with django_assert_max_num_queries(0):
            discounted_fixed_price = product_option_calculate_discounted_price(
                option=option_2, discount=fixed_price_discount
            )

        assert discounted_percentage_price == Decimal("70.00")
        assert discounted_fixed_price == Decimal("100.00")

    def test_selector_product_get_active_discount(
        self, django_assert_max_num_queries
    ) -> None:
        """
        Test that the product_get_active_discount returns expected
        output within query limits.
        """

        product_1 = create_product(product_name="Product 1")
        create_product_option(product=product_1, gross_price=Decimal("200.00"))
        create_product_option(product=product_1, gross_price=Decimal("300.00"))
        create_product_option(product=product_1, gross_price=Decimal("400.00"))
        create_product_option(product=product_1, gross_price=Decimal("500.00"))

        product_2 = create_product(product_name="Product 2")
        option_2 = create_product_option(
            product=product_2, gross_price=Decimal("100.00")
        )

        product_3 = create_product(product_name="Product 3")
        create_product_option(product=product_3, gross_price=Decimal("200.00"))

        create_discount(
            discount_gross_percentage=Decimal("0.20"),
            products=[product_1],
            product_options=[option_2],
            active_at=timezone.now(),
            active_to=timezone.now() + timedelta(minutes=10),
        )

        # Uses 4 queries:
        # - 1x for getting product options in fallback
        # - 1x for prefetching options discounts
        # - 1x for getting product discounts in fallback
        # - 1x for calculating lowest option price
        with django_assert_max_num_queries(4):
            product_1_discount = product_get_active_discount(product=product_1)

        assert product_1_discount is not None
        assert product_1_discount.is_discounted is True
        assert product_1_discount.discounted_gross_price == Decimal("160.00")

        # Uses 4 queries:
        # - 1x for getting product options in fallback
        # - 1x for prefetching options discounts
        # - 1x for getting product discounts in fallback
        # - 1x for calculating lowest option price
        with django_assert_max_num_queries(4):
            product_2_discount = product_get_active_discount(product=product_2)

        assert product_2_discount is not None
        assert product_2_discount.is_discounted is True
        assert product_2_discount.discounted_gross_price == Decimal("80.00")

        # Uses 4 queries:
        # - 1x for getting product options in fallback
        # - 1x for prefetching options discounts
        # - 1x for getting product discounts in fallback
        # - 1x for calculating lowest option price
        with django_assert_max_num_queries(4):
            product_3_discount = product_get_active_discount(product=product_3)

        assert product_3_discount is None

        products_prefetched = (
            Product.objects.all()
            .with_active_product_discounts()
            .with_active_options_discounts()
            .annotate_from_price()
            .order_by("created_at")
        )

        assert len(products_prefetched) == 3

        # Should only use prefetched attributes, and should not hit db.
        with django_assert_max_num_queries(0):
            prefetched_product_1_discount = product_get_active_discount(
                product=products_prefetched[0]
            )

        assert prefetched_product_1_discount is not None
        assert prefetched_product_1_discount.is_discounted is True
        assert prefetched_product_1_discount.discounted_gross_price == Decimal("160.00")

        # Should only use prefetched attributes, and should not hit db.
        with django_assert_max_num_queries(0):
            prefetched_product_2_discount = product_get_active_discount(
                product=products_prefetched[1]
            )

        assert prefetched_product_2_discount is not None
        assert prefetched_product_2_discount.is_discounted is True
        assert prefetched_product_2_discount.discounted_gross_price == Decimal("80.00")

        # Should only use prefetched attributes, and should not hit db.
        with django_assert_max_num_queries(0):
            prefetched_product_3_discount = product_get_active_discount(
                product=products_prefetched[2]
            )

        assert prefetched_product_3_discount is None

    def test_selector_product_option_get_active_discount(  # pylint: disable=too-many-locals, too-many-statements
        self, django_assert_max_num_queries
    ) -> None:
        """
        Test that the product_option_get_active_discount returns expected
        output within query limits.
        """

        product_1 = create_product(product_name="Product 1")
        option_1 = create_product_option(
            product=product_1, gross_price=Decimal("100.00")
        )
        option_2 = create_product_option(
            product=product_1, gross_price=Decimal("200.00")
        )
        option_3 = create_product_option(
            product=product_1, gross_price=Decimal("300.00")
        )

        product_2 = create_product(product_name="Product 2")
        option_4 = create_product_option(
            product=product_2, gross_price=Decimal("400.00")
        )
        option_5 = create_product_option(
            product=product_2, gross_price=Decimal("200.00")
        )

        create_discount(
            name="Fixed 100",
            discount_gross_price=Decimal("100.00"),
            product_options=[option_3],
            active_at=timezone.now(),
            active_to=timezone.now() + timedelta(minutes=10),
        )

        create_discount(
            name="20% off",
            discount_gross_percentage=Decimal("0.20"),
            products=[product_1],
            product_options=[option_4],
            active_at=timezone.now(),
            active_to=timezone.now() + timedelta(minutes=10),
        )

        # Uses 3 queries:
        # - 1x for getting discounts for option
        # - 1x for getting discounts for product
        # - 1x for calculating discount price
        with django_assert_max_num_queries(3):
            option_1_discount = product_option_get_active_discount(
                product_option=option_1
            )

        assert option_1_discount is not None
        assert option_1_discount.is_discounted is True
        assert option_1_discount.discounted_gross_price == Decimal("80.00")

        # Uses 3 queries:
        # - 1x for getting discounts for option
        # - 1x for getting discounts for product
        # - 1x for calculating discount price
        with django_assert_max_num_queries(3):
            option_2_discount = product_option_get_active_discount(
                product_option=option_2
            )

        assert option_2_discount is not None
        assert option_2_discount.is_discounted is True
        assert option_2_discount.discounted_gross_price == Decimal("160.00")

        # Uses 3 queries:
        # - 1x for getting discounts for option
        # - 1x for getting discounts for product
        # - 1x for calculating discount price
        with django_assert_max_num_queries(3):
            option_3_discount = product_option_get_active_discount(
                product_option=option_3
            )

        assert option_3_discount is not None
        assert option_3_discount.is_discounted is True
        # option_3 has a more specific discount active than on the product level,
        # therefore that should be used.
        assert option_3_discount.discounted_gross_price == Decimal("100.00")

        # Uses 3 queries:
        # - 1x for getting discounts for option
        # - 1x for getting discounts for product
        # - 1x for calculating discount price
        with django_assert_max_num_queries(3):
            option_4_discount = product_option_get_active_discount(
                product_option=option_4
            )

        assert option_4_discount is not None
        assert option_4_discount.is_discounted is True
        assert option_4_discount.discounted_gross_price == Decimal("320.00")

        # Uses 3 queries:
        # - 1x for getting discounts for option
        # - 1x for getting discounts for product
        # - 1x for calculating discount price
        with django_assert_max_num_queries(3):
            option_5_discount = product_option_get_active_discount(
                product_option=option_5
            )

        assert option_5_discount is None

        prefetched_products = list(
            Product.objects.all()
            .with_available_options_and_option_discounts()
            .with_active_product_discounts()
            .order_by("created_at")
        )

        def _get_prefetched_option(
            product: Product, option: ProductOption
        ) -> ProductOption:
            product_index = prefetched_products.index(product)
            return [
                o
                for o in prefetched_products[product_index].available_options
                if o.id == option.id
            ][0]

        # Should use prefetched attributes, and not hit db.
        with django_assert_max_num_queries(0):
            option_1_prefetched_discount = product_option_get_active_discount(
                product_option=_get_prefetched_option(product_1, option_1)
            )

        assert option_1_prefetched_discount is not None
        assert option_1_prefetched_discount.is_discounted is True
        assert option_1_prefetched_discount.discounted_gross_price == Decimal("80.00")

        # Should use prefetched attributes, and not hit db.
        with django_assert_max_num_queries(0):
            option_2_prefetched_discount = product_option_get_active_discount(
                product_option=_get_prefetched_option(product_1, option_2)
            )

        assert option_2_prefetched_discount is not None
        assert option_2_prefetched_discount.is_discounted is True
        assert option_2_prefetched_discount.discounted_gross_price == Decimal("160.00")

        # Should use prefetched attributes, and not hit db.
        with django_assert_max_num_queries(0):
            option_3_prefetched_discount = product_option_get_active_discount(
                product_option=_get_prefetched_option(product_1, option_3)
            )

        assert option_3_prefetched_discount is not None
        assert option_3_prefetched_discount.is_discounted is True
        # option_3 has a more specific discount active than on the product level,
        # therefore that should be used.
        assert option_3_prefetched_discount.discounted_gross_price == Decimal("100.00")

        # Should use prefetched attributes, and not hit db.
        with django_assert_max_num_queries(0):
            option_4_prefetched_discount = product_option_get_active_discount(
                product_option=_get_prefetched_option(product_2, option_4)
            )

        assert option_4_prefetched_discount is not None
        assert option_4_prefetched_discount.is_discounted is True
        assert option_4_prefetched_discount.discounted_gross_price == Decimal("320.00")

        # Should use prefetched attributes, and not hit db.
        with django_assert_max_num_queries(0):
            option_5_prefetched_discount = product_option_get_active_discount(
                product_option=_get_prefetched_option(product_2, option_5)
            )

        assert option_5_prefetched_discount is None
