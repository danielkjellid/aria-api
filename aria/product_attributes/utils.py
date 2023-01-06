from decimal import Decimal

from django.utils.translation import gettext as _

from aria.core.exceptions import ApplicationError
from aria.product_attributes.records import SizeRecord


def size_clean_and_validate_value(
    *,
    width: Decimal | float | None = None,
    height: Decimal | float | None = None,
    depth: Decimal | float | None = None,
    circumference: Decimal | float | None = None,
) -> SizeRecord:
    """
    Clean size values and validate that param combinations are correct.
    """

    if all(param is None for param in (width, height, depth, circumference)):
        raise ValueError("All size params cannot be None!")

    # Convert zero's to None to avoid having dangling 0's in the DB creating multiple
    # of the "same" size.
    width = width if width != 0 else None
    height = height if height != 0 else None
    depth = depth if depth != 0 else None
    circumference = circumference if circumference else None

    size_to_clean = {
        "width": Decimal(width) if width else None,
        "height": Decimal(height) if height else None,
        "depth": Decimal(depth) if depth else None,
        "circumference": Decimal(circumference) if circumference else None,
    }

    _size_validate(**size_to_clean)

    return SizeRecord(**size_to_clean)


def size_clean_and_validate_values(*, sizes: list[SizeRecord]) -> list[SizeRecord]:
    """
    Clean size values for a list of sizes and validate that param combinations are
    correct.
    """

    cleaned_sizes = []

    for size in sizes:
        cleaned_size = size_clean_and_validate_value(
            width=size.width,
            height=size.height,
            depth=size.depth,
            circumference=size.circumference,
        )

        cleaned_sizes.append(cleaned_size)

    return cleaned_sizes


def _size_validate(
    *,
    width: Decimal | None = None,
    height: Decimal | None = None,
    depth: Decimal | None = None,
    circumference: Decimal | None = None,
) -> None:
    """
    Validate that the correct combination of values is present. For example, we do not
    want to populate certain values based on conditions.
    """

    # Make sure that circumferential sizes only has the circumference param sent in.
    if circumference is not None and any(
        param is not None for param in (width, height, depth)
    ):

        extra_dict = {}

        if width is not None:
            extra_dict["width"] = _(
                "Field cannot be specified when making a circumferential size"
            )
        if height is not None:
            extra_dict["height"] = _(
                "Field cannot be specified when making a circumferential size"
            )
        if depth is not None:
            extra_dict["depth"] = _(
                "Field cannot be specified when making a circumferential size"
            )

        raise ApplicationError(
            message=_(
                "Width, height or depth cannot be specified when making a "
                "circumferential size."
            ),
            extra=extra_dict,
        )

    # Make sure that normal sizes at least have width and height specified.
    if circumference is None and any(param is None for param in (width, height)):
        raise ApplicationError(
            message=_(
                "Width and height needs to be specified when not making a "
                "circumferential size."
            ),
            extra={
                "width": _("field required."),
                "height": _("field required."),
            },
        )
