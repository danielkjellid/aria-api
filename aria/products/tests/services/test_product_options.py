import pytest

pytestmark = pytest.mark.django_db


class TestProductOptionsServices:
    def test_product_option_create(self, django_assert_max_num_queries):
        assert False
