from decimal import Decimal

from aria.product_attributes.models import Size


def create_size(
    width: Decimal | None = None,
    height: Decimal | None = None,
    depth: Decimal | None = None,
    circumference: Decimal | None = None,
) -> Size:
    """
    Test util that creates a size instance.
    """

    if all(param is None for param in (width, height, depth, circumference)):
        raise ValueError("All args cannot be None!")

    size = Size.objects.create(
        width=width, height=height, depth=depth, circumference=circumference
    )

    return size
