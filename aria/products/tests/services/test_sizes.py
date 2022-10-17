import pytest

pytestmark = pytest.mark.django_db


class TestProductSizesServices:
    def test_service_size_create(self, django_assert_max_num_queries):
        assert False

    def test_service_size_bulk_create(self, django_assert_max_num_queries):
        assert False

    def test_service_size_get_or_create(self, django_assert_max_num_queries):
        assert False

    def test_service__size_validate(self, django_assert_max_num_queries):
        assert False

    def test_service_size_clean_and_validate_value(self, django_assert_max_num_queries):
        assert False

    def test_service_size_clean_and_validate_values(
        self, django_assert_max_num_queries
    ):
        assert False
