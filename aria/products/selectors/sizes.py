from aria.products.models import Size
from aria.products.records import ProductSizeRecord
from aria.products.types import SizeDict


def size_list_from_mapped_values(values: list[SizeDict]) -> list[ProductSizeRecord]:

    aggregated_values = {
        k: [val.get(k) for val in values] for k in set().union(*values)
    }

    widths = aggregated_values.get("width", [])
    heights = aggregated_values.get("height", [])
    depths = aggregated_values.get("depth", [])
    circumferences = aggregated_values.get("circumference", [])

    sizes = Size.objects.filter(
        width__in=widths,
        height__in=heights,
        depth__in=depths,
        circumference__in=circumferences,
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
