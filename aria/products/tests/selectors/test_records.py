import pytest

from aria.products.models import Product
from aria.products.selectors.records import product_list_record
from aria.products.tests.utils import create_product

pytestmark = pytest.mark.django_db


class TestProductRecordsSelectors:
    def test_selector_product_list_record(self, django_assert_max_num_queries):
        """
        Make sure the product_list_record selector enforeces the usage
        of prefetched values and that it does not cause any queries.
        """

        create_product(product_name="Product 1")
        create_product(product_name="Product 2")
        create_product(product_name="Product 3")

        products = Product.objects.all()

        assert len(products) == 3

        with django_assert_max_num_queries(0):
            with pytest.raises(AssertionError):
                product_list_record(products[0])
                product_list_record(products[1])
                product_list_record(products[2])

        products = products.preload_for_list()

        assert len(products) == 3

        with django_assert_max_num_queries(0):
            product_list_record(products[0])
            product_list_record(products[1])
            product_list_record(products[2])
