from decimal import Decimal
from typing import Any

from django.db.models import Q

from aria.products.models import Size
from aria.products.records import ProductSizeRecord


def size_list_from_mapped_values(
    values: list[dict[str, Any]]
) -> list[ProductSizeRecord]:
    """
    Map a list of unknown sizes to existing size instances in the db, and return a list
    of mapped instances.
    """

    # Aggregate all values base on key. Will return something like:
    # [{"width": [30.0, 20.0, 10.0], "height": [11.0, 20.0]...}...].
    aggregated_values = {
        k: [Decimal(val.get(k)) for val in values if val.get(k) is not None]  # type: ignore # pylint: disable=line-too-long
        for k in set().union(*values)
    }

    widths = aggregated_values.get("width", [])
    heights = aggregated_values.get("height", [])
    depths = aggregated_values.get("depth", [])
    circumferences = aggregated_values.get("circumference", [])

    sizes = (
        Size.objects.filter(
            Q(width__in=widths)
            | Q(height__in=heights)
            | Q(depth__in=depths)
            | Q(circumference__in=circumferences)
        )
        .distinct("id")
        .order_by("-id")
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
