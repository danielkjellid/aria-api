import pytest

from aria.products.records import ProductColorRecord
from aria.products.selectors.colors import color_list
from aria.products.tests.utils import create_color

pytestmark = pytest.mark.django_db


class TestProductColorsSelectors:
    def test_selector_color_list(self, django_assert_max_num_queries):
        """
        Test that the color_list selector returns expected output withing query limits.
        """

        color_1 = create_color(name="Test color 1", color_hex="#FFFFFF")
        color_2 = create_color(name="Test color 2", color_hex="#CCCCCC")
        color_3 = create_color(name="Test color 3", color_hex="#BBBBBB")
        color_4 = create_color(name="Test color 4", color_hex="#333333")

        expected_output = [
            ProductColorRecord(id=color_4.id, name="Test color 4", color_hex="#333333"),
            ProductColorRecord(id=color_3.id, name="Test color 3", color_hex="#BBBBBB"),
            ProductColorRecord(id=color_2.id, name="Test color 2", color_hex="#CCCCCC"),
            ProductColorRecord(id=color_1.id, name="Test color 1", color_hex="#FFFFFF"),
        ]

        with django_assert_max_num_queries(1):
            colors = color_list()

        assert colors == expected_output
