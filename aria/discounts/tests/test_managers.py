from datetime import timedelta
from decimal import Decimal

from django.utils import timezone

import pytest

from aria.discounts.models import Discount
from aria.discounts.tests.utils import create_discount

pytestmark = pytest.mark.django_db


class TestDiscountQuerySetManager:

    model = Discount

    def test_active(self, django_assert_max_num_queries) -> None:
        discount_1 = create_discount(
            name="Discount 1",
            discount_gross_percentage=Decimal(0.20),
            active_at=None,
            active_to=timezone.now() + timedelta(minutes=10),
        )
        discount_2 = create_discount(
            name="Discount 2",
            discount_gross_percentage=Decimal(0.20),
            active_at=timezone.now(),
            active_to=None,
        )
        discount_3 = create_discount(
            name="Discount 3",
            discount_gross_percentage=Decimal(0.20),
            active_at=timezone.now(),
            active_to=timezone.now() + timedelta(minutes=10),
            maximum_sold_quantity=10,
            total_sold_quantity=10,
        )

        # Performs 1 query for filtering.
        with django_assert_max_num_queries(1):
            active_discounts = Discount.objects.active()

            assert len(active_discounts) == 2
            assert list(active_discounts) == [discount_1, discount_2]
            assert discount_3 not in active_discounts
