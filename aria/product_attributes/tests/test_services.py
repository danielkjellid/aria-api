from decimal import Decimal

import pytest

from aria.product_attributes.models import Size
from aria.product_attributes.records import SizeRecord
from aria.product_attributes.services import (
    size_bulk_create,
    size_create,
    size_get_or_create,
)
from aria.product_attributes.tests.utils import create_size

pytestmark = pytest.mark.django_db


class TestProductAttributesServices:
    def test_service_size_create(self, django_assert_max_num_queries):
        """
        Test that the size_create service creates a size within query limits.
        """

        with django_assert_max_num_queries(1):
            size_record = size_create(
                width=Decimal("10.0"),
                height=Decimal("20.0"),
                depth=Decimal("0"),
                circumference=None,
            )

        assert size_record.width == Decimal("10.0")
        assert size_record.height == Decimal("20.0")
        assert size_record.depth is None
        assert size_record.circumference is None

    def test_service_size_bulk_create(self, django_assert_max_num_queries):
        """
        Test that the size_bulk_create service creates unique, non-existant,
        sizes in bulk effectively.
        """

        create_size(
            width=Decimal("10.0"),
            height=Decimal("20.0"),
            depth=None,
            circumference=None,
        )
        create_size(
            width=Decimal("5.0"),
            height=Decimal("10.0"),
            depth=Decimal("10.0"),
            circumference=None,
        )

        sizes_in_db_count = Size.objects.count()

        sizes_to_create = [
            SizeRecord(width=10.0, height=20.0),
            SizeRecord(width=5.0, height=10.0, depth=10.0),
            SizeRecord(width=25.0, height=90.0, depth=0),
            SizeRecord(width=20.0, height=45.0, depth=5.0),
            SizeRecord(width=18.0, height=11.0, depth=10.0),
            SizeRecord(circumference=30.0),
        ]

        # Uses 2 queries; 1 for bulk creating and 1 for retrieving sizes.
        with django_assert_max_num_queries(3):
            sizes = size_bulk_create(sizes=sizes_to_create)

        assert len(sizes) == len(sizes_to_create)
        assert (
            Size.objects.count() == sizes_in_db_count + 4
        )  # 4 should've been created.

    def test_service_size_get_or_create(self, django_assert_max_num_queries):
        """
        Test that the size_get_or_create returns correct output within query limits.
        """

        existing_site = create_size(
            width=Decimal("10.0"),
            height=Decimal("20.0"),
            depth=None,
            circumference=None,
        )

        sizes_in_db_count = Size.objects.count()

        with django_assert_max_num_queries(1):
            existing_size_from_get = size_get_or_create(
                width=existing_site.width,
                height=existing_site.height,
                depth=existing_site.depth,
                circumference=existing_site.circumference,
            )

        assert existing_size_from_get.id == existing_site.id
        assert Size.objects.count() == sizes_in_db_count  # Nothing was created.

        with django_assert_max_num_queries(2):
            non_existent_size = size_get_or_create(
                width=Decimal("12.0"),
                height=Decimal("10.0"),
                depth=Decimal("20.0"),
                circumference=None,
            )

        assert non_existent_size is not None
        assert Size.objects.count() == sizes_in_db_count + 1
