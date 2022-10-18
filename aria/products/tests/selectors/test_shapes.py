import pytest

from aria.products.records import ProductShapeRecord
from aria.products.selectors.shapes import shape_list
from aria.products.tests.utils import create_shape

pytestmark = pytest.mark.django_db


class TestProductShapesSelectors:
    def test_selector_shape_list(self, django_assert_max_num_queries):
        """
        Test that the shapes_list selector returns expected output within query limits.
        """

        shape_1 = create_shape(name="Shape 1")
        shape_2 = create_shape(name="Shape 2")
        shape_3 = create_shape(name="Shape 3")
        shape_4 = create_shape(name="Shape 4")

        expected_output = [
            ProductShapeRecord(
                id=shape_4.id,
                name="Shape 4",
                image=shape_4.image.url if shape_4.image else None,
            ),
            ProductShapeRecord(
                id=shape_3.id,
                name="Shape 3",
                image=shape_3.image.url if shape_3.image else None,
            ),
            ProductShapeRecord(
                id=shape_2.id,
                name="Shape 2",
                image=shape_2.image.url if shape_2.image else None,
            ),
            ProductShapeRecord(
                id=shape_1.id,
                name="Shape 1",
                image=shape_1.image.url if shape_1.image else None,
            ),
        ]

        with django_assert_max_num_queries(1):
            shapes = shape_list()

        assert shapes == expected_output
