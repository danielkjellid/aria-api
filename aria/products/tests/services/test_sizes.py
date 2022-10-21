from decimal import Decimal

import pytest

from aria.core.exceptions import ApplicationError
from aria.products.models import Size
from aria.products.services.sizes import (
    _size_validate,
    size_bulk_create,
    size_clean_and_validate_value,
    size_create,
    size_get_or_create,
)
from aria.products.tests.utils import create_size

pytestmark = pytest.mark.django_db


class TestProductSizesServices:
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
            {"width": 10.0, "height": 20.0, "depth": None, "circumference": None},
            {"width": 5.0, "height": 10.0, "depth": 10.0, "circumference": None},
            {"width": 25.0, "height": 90.0, "depth": 0, "circumference": None},
            {"width": 20.0, "height": 45.0, "depth": 5.0, "circumference": None},
            {"width": 18.0, "height": 11.0, "depth": 10.0, "circumference": None},
            {"width": None, "height": None, "depth": None, "circumference": 30.0},
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

    def test_service__size_validate(self):
        """
        Test that the _size_validate util raises expected exceptions.
        """

        # Width, height or depth cannot be specified when making a circumferential size:
        with pytest.raises(ApplicationError):
            _size_validate(width=Decimal("10.0"), circumference=Decimal("20.0"))

        with pytest.raises(ApplicationError):
            _size_validate(height=Decimal("15.0"), circumference=Decimal("20.0"))

        with pytest.raises(ApplicationError):
            _size_validate(depth=Decimal("20.0"), circumference=Decimal("20.0"))

        with pytest.raises(ApplicationError):
            _size_validate(
                height=Decimal("10.0"),
                width=Decimal("10.0"),
                circumference=Decimal("20.0"),
            )

        # Width and height needs to be specified when not making a circumferential size:
        with pytest.raises(ApplicationError):
            _size_validate(
                height=Decimal("10.0"),
                width=None,
                depth=Decimal("10.0"),
                circumference=None,
            )

        with pytest.raises(ApplicationError):
            _size_validate(
                height=None,
                width=Decimal("10.0"),
                depth=Decimal("10.0"),
                circumference=None,
            )

        with pytest.raises(ApplicationError):
            _size_validate(
                height=None,
                width=None,
                depth=Decimal("10.0"),
                circumference=None,
            )

    def test_service_size_clean_and_validate_value(self, django_assert_max_num_queries):
        """
        Test that the size_clean_and_validate util clean's values appropriately.
        Validation testing is handled in the test above.
        """

        # Zeros input as args should be converted to None.
        with django_assert_max_num_queries(0):
            with_zeros = size_clean_and_validate_value(
                width=Decimal("14.00"), height=Decimal("20.0"), depth=Decimal("0")
            )

        assert with_zeros.width == Decimal("14.0")
        assert with_zeros.height == Decimal("20.0")
        assert with_zeros.depth is None  # We don't want dangling 0's in the db
        assert with_zeros.circumference is None

        with django_assert_max_num_queries(0):
            with pytest.raises(ValueError):
                size_clean_and_validate_value(
                    width=None, height=None, depth=None, circumference=None
                )
