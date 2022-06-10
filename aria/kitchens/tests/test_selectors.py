import pytest

from aria.kitchens.selectors import kitchen_available_list, kitchen_detail
from aria.kitchens.tests.utils import create_kitchen
from aria.products.enums import ProductStatus

pytestmark = pytest.mark.django_db


class TestKitchensSelectors:
    def test_kitchen_available_list(self, django_assert_max_num_queries) -> None:
        """
        Test the kitchen_available_list selector returns expected response
        within query limit.
        """

        available_kitchen_1 = create_kitchen(name="Kitchen 1")
        available_kitchen_2 = create_kitchen(name="Kitchen 2")
        available_kitchen_3 = create_kitchen(name="Kitchen 3")
        unavailable_kitchen = create_kitchen(
            name="Kitchen 4", status=ProductStatus.DRAFT
        )

        # Uses 1 query to get list of kitchens and related suppliers.
        with django_assert_max_num_queries(1):
            available_kitchens = kitchen_available_list()

        sorted_available_kitchens = sorted(available_kitchens, key=lambda k: k.id)

        assert len(sorted_available_kitchens) == 3  # Only the 3 available
        assert sorted_available_kitchens[0].id == available_kitchen_1.id
        assert sorted_available_kitchens[1].id == available_kitchen_2.id
        assert sorted_available_kitchens[2].id == available_kitchen_3.id
        assert unavailable_kitchen.id not in [
            kitchen.id for kitchen in sorted_available_kitchens
        ]

    def test_kitchen_detail(self, django_assert_max_num_queries) -> None:
        """
        Test the kitchen_detail selector returns expected response
        within query limit for a specific kitchen.
        """

        kitchen = create_kitchen()

        # Uses 7 queries:
        # - 1 for getting kitchen + supplier
        # - 6 for prefetching related objects.
        with django_assert_max_num_queries(7):
            fetched_kitchen = kitchen_detail(kitchen_id=kitchen.id)

        assert fetched_kitchen.id == kitchen.id
        assert len(fetched_kitchen.silk_variants) == len(kitchen.silk_variants.all())
        assert len(fetched_kitchen.decor_variants) == len(kitchen.decor_variants.all())
        assert len(fetched_kitchen.plywood_variants) == len(
            kitchen.plywood_variants.all()
        )
        assert len(fetched_kitchen.laminate_variants) == len(
            kitchen.laminate_variants.all()
        )
        assert len(fetched_kitchen.exclusive_variants) == len(
            kitchen.exclusive_variants.all()
        )
        assert len(fetched_kitchen.trend_variants) == len(kitchen.trend_variants.all())
