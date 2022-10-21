import tempfile
from decimal import Decimal

from aria.product_attributes.models import Shape, Size


def create_shape(*, name: str) -> Shape:
    """
    Test util that creates a shape instance.
    """

    shape, _created = Shape.objects.get_or_create(name=name)

    with tempfile.NamedTemporaryFile(suffix=".jpg") as file:
        shape.image = file.name

    shape.save()

    return shape


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
