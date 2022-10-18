from aria.products.models import Color
from aria.products.records import ProductColorRecord


def color_list() -> ProductColorRecord:
    """
    Returns a list of all colors in the application.
    """

    colors = Color.objects.all().order_by("-id")

    return [
        ProductColorRecord(
            id=color.id,
            name=color.name,
            color_hex=color.color_hex,
        )
        for color in colors
    ]
