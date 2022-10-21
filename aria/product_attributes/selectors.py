from decimal import Decimal

from django.db.models import Q

from aria.product_attributes.models import Size
from aria.product_attributes.records import SizeDetailRecord, SizeRecord


def size_list_from_mapped_values(values: list[SizeRecord]) -> list[SizeDetailRecord]:
    """
    Map a list of unknown sizes to existing size instances in the db, and return a list
    of mapped instances.
    """

    dict_records = [size_record.dict() for size_record in values]

    # Aggregate all values base on key. Will return something like:
    # [{"width": [30.0, 20.0, 10.0], "height": [11.0, 20.0]...}...].
    aggregated_values = {
        k: [Decimal(val.get(k)) for val in dict_records if val.get(k) is not None]  # type: ignore # pylint: disable=line-too-long
        for k in set().union(*dict_records)
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
        SizeDetailRecord(
            id=size.id,
            name=size.name,
            width=size.width,
            height=size.height,
            depth=size.depth,
            circumference=size.circumference,
        )
        for size in sizes
    ]
