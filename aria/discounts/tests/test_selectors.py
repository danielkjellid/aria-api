import pytest

pytestmark = pytest.mark.django_db


class TestDiscountsSelectors:
    def test_discount_active_list(self, django_assert_max_num_queries):
        """
        Test that the discount_active_list selector returns expected output
        withing query limits.
        """

        assert False
