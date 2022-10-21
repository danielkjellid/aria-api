from decimal import Decimal

import pytest

from aria.core.exceptions import ApplicationError
from aria.product_attributes.utils import _size_validate, size_clean_and_validate_value


class TestProductAttributesUtils:
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

    def test_service_size_clean_and_validate_value(self):
        """
        Test that the size_clean_and_validate util clean's values appropriately.
        Validation testing is handled in the test above.
        """

        # Zeros input as args should be converted to None.
        with_zeros = size_clean_and_validate_value(
            width=Decimal("14.00"), height=Decimal("20.0"), depth=Decimal("0")
        )

        assert with_zeros.width == Decimal("14.0")
        assert with_zeros.height == Decimal("20.0")
        assert with_zeros.depth is None  # We don't want dangling 0's in the db
        assert with_zeros.circumference is None

        with pytest.raises(ValueError):
            size_clean_and_validate_value(
                width=None, height=None, depth=None, circumference=None
            )
