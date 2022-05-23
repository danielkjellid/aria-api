from django.db.models import Q

from aria.core.selectors import base_header_image_record, base_list_image_record
from aria.kitchens.models import Kitchen
from aria.kitchens.schemas.records import (
    KitchenDetailRecord,
    KitchenSupplierRecord,
    KitchenVariantColorRecord,
    KitchenVariantRecord,
)


def kitchen_detail(
    *, kitchen_id: int | None = None, kitchen_slug: str | None = None
) -> KitchenDetailRecord | None:
    """
    Get the detailed representation of a single product based on either
    id or slug, although one of them has to be provided.
    """

    kitchen = (
        Kitchen.objects.filter(Q(id=kitchen_id) | Q(slug=kitchen_slug))
        .select_related("supplier")
        .prefetch_related(
            "silk_variants",
            "decor_variants",
            "plywood_variants",
            "laminate_variants",
            "exclusive_variants",
            "trend_variants",
        )
        .first()
    )

    if not kitchen:
        return None

    record = KitchenDetailRecord(
        id=kitchen.id,
        name=kitchen.name,
        slug=kitchen.slug,
        supplier=KitchenSupplierRecord(
            id=kitchen.supplier.id, name=kitchen.supplier.name
        ),
        description=kitchen.description,
        extra_description=kitchen.extra_description,
        example_from_price=kitchen.example_from_price,
        can_be_painted=kitchen.can_be_painted,
        silk_variants=[
            KitchenVariantColorRecord(id=obj.id, name=obj.name, color_hex=obj.color_hex)
            for obj in kitchen.silk_variants.all()
        ],
        decor_variants=[
            KitchenVariantRecord(id=obj.id, name=obj.name, image=obj.image.url)
            for obj in kitchen.decor_variants.all()
        ],
        plywood_variants=[
            KitchenVariantRecord(id=obj.id, name=obj.name, image=obj.image.url)
            for obj in kitchen.plywood_variants.all()
        ],
        laminate_variants=[
            KitchenVariantColorRecord(id=obj.id, name=obj.name, color_hex=obj.color_hex)
            for obj in kitchen.laminate_variants.all()
        ],
        exclusive_variants=[
            KitchenVariantColorRecord(id=obj.id, name=obj.name, color_hex=obj.color_hex)
            for obj in kitchen.exclusive_variants.all()
        ],
        trend_variants=[
            KitchenVariantColorRecord(id=obj.id, name=obj.name, color_hex=obj.color_hex)
            for obj in kitchen.trend_variants.all()
        ],
        images=base_header_image_record(instance=kitchen),
        list_images=base_list_image_record(instance=kitchen),
    )

    return record