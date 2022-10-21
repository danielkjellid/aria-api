from decimal import Decimal
from unittest.mock import ANY

import pytest

from aria.product_attributes.records import SizeDetailRecord, SizeRecord
from aria.product_attributes.selectors import size_list_from_mapped_values
from aria.product_attributes.tests.utils import create_size

pytestmark = pytest.mark.django_db


class TestProductAttributesSelectors:
    def test_selector_size_list_from_mapped_values(self, django_assert_max_num_queries):
        """
        Test that the size_list_from_mapped_values correctly mappes unique values to
        record instances.
        """

        size_1 = create_size(
            width=Decimal("20.0"), height=Decimal("40.0"), depth=Decimal("10.0")
        )
        size_2 = create_size(
            width=Decimal("30.0"), height=Decimal("40.0"), depth=Decimal("5.0")
        )
        size_3 = create_size(
            width=Decimal("20.0"), height=Decimal("10.0"), depth=Decimal("5.0")
        )
        size_4 = create_size(width=Decimal("25.0"), height=Decimal("35.0"))
        size_5 = create_size(
            width=Decimal("80.5"), height=Decimal("39.0"), depth=Decimal("12.0")
        )
        size_6 = create_size(circumference=Decimal("30.0"))
        size_7 = create_size(circumference=Decimal("40.0"))
        size_8 = create_size(circumference=Decimal("14.0"))

        size_values_to_map = [
            SizeRecord(width=20.0, height=40.0, depth=10.0),
            SizeRecord(width=30.0, height=40.0, depth=5.0),
            SizeRecord(width=20.0, height=10.0, depth=5.0),
            SizeRecord(width=25.0, height=35.0, depth=12.0),
            SizeRecord(width=80.5, height=35.0, depth=12.0),
            SizeRecord(circumference=30.0),
            SizeRecord(circumference=30.0),
            SizeRecord(circumference=40.0),
            SizeRecord(circumference=14.0),
        ]

        expected_output = [
            SizeDetailRecord.construct(
                id=size_8.id,
                width=None,
                height=None,
                depth=None,
                circumference=Decimal("14"),
                name=ANY,
            ),
            SizeDetailRecord.construct(
                id=size_7.id,
                width=None,
                height=None,
                depth=None,
                circumference=Decimal("40"),
                name=ANY,
            ),
            SizeDetailRecord.construct(
                id=size_6.id,
                width=None,
                height=None,
                depth=None,
                circumference=Decimal("30"),
                name=ANY,
            ),
            SizeDetailRecord.construct(
                id=size_5.id,
                width=Decimal("80.5"),
                height=Decimal("39.0"),
                depth=Decimal("12.0"),
                circumference=None,
                name=ANY,
            ),
            SizeDetailRecord.construct(
                id=size_4.id,
                width=Decimal("25.0"),
                height=Decimal("35.0"),
                depth=None,
                circumference=None,
                name=ANY,
            ),
            SizeDetailRecord.construct(
                id=size_3.id,
                width=Decimal("20.0"),
                height=Decimal("10.0"),
                depth=Decimal("5.0"),
                circumference=None,
                name=ANY,
            ),
            SizeDetailRecord.construct(
                id=size_2.id,
                width=Decimal("30.0"),
                height=Decimal("40.0"),
                depth=Decimal("5.0"),
                circumference=None,
                name=ANY,
            ),
            SizeDetailRecord.construct(
                id=size_1.id,
                width=Decimal("20.0"),
                height=Decimal("40.0"),
                depth=Decimal("10.0"),
                circumference=None,
                name=ANY,
            ),
        ]

        with django_assert_max_num_queries(1):
            mapped_values = size_list_from_mapped_values(values=size_values_to_map)

        # There is 1 duplicate in the list, circumference 30.0, so make sure that this
        # is not returned twice.
        assert len(mapped_values) == len(size_values_to_map) - 1
        assert mapped_values == expected_output
