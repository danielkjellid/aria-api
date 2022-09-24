from aria.products.models import Size
from aria.products.records import ProductSizeRecord


def size_distinct_list() -> list[ProductSizeRecord]:
    """
    Returns a list of all sizes in the application.
    """

    sizes = (
        Size.objects.all()
        .distinct("width", "height", "depth", "circumference")
        .order_by("width", "height", "depth", "circumference", "-id")
    )

    return [
        ProductSizeRecord(
            id=size.id,
            width=size.width,
            height=size.height,
            depth=size.depth,
            circumference=size.circumference,
            name=size.name,
        )
        for size in sizes
    ]
