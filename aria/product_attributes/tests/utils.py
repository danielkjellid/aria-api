import tempfile
from decimal import Decimal

from aria.product_attributes.models import Color, Material, Room, Shape, Size, Variant


def create_color(*, name: str, color_hex: str) -> Color:
    """
    Test util that creates a color instance.
    """

    color, _created = Color.objects.get_or_create(
        name=name, defaults={"color_hex": color_hex}
    )

    return color


def create_material(*, name: str) -> Material:
    """
    Test util that creates a material instance.
    """

    material, _created = Material.objects.get_or_create(name=name)

    return material


def create_room(*, name: str) -> Room:
    """
    Test util that creates a room instance.
    """

    room, _created = Room.objects.get_or_create(name=name)

    return room


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


def create_variant(
    *, name: str = "Example variant", is_standard: bool = False
) -> Variant:
    """
    Test util that creates a variant instance.
    """

    variant = Variant.objects.create(name=name, is_standard=is_standard)

    with tempfile.NamedTemporaryFile(suffix=".jpg") as file:
        variant.image = file.name

    variant.save()

    return variant
