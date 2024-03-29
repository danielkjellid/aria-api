from django.db.models import Q

from aria.files.records import BaseCollectionListImageRecord, BaseHeaderImageRecord
from aria.kitchens.models import Kitchen
from aria.kitchens.records import (
    KitchenDetailRecord,
    KitchenRecord,
    KitchenSupplierRecord,
    KitchenVariantColorRecord,
    KitchenVariantRecord,
)


def kitchen_record(*, kitchen: Kitchen) -> KitchenRecord:
    """
    Get the record representation for a single kitchen instance.
    """

    return KitchenRecord(
        id=kitchen.id,
        name=kitchen.name,
        slug=kitchen.slug,
        supplier=KitchenSupplierRecord(
            id=kitchen.supplier.id, name=kitchen.supplier.name
        ),
        thumbnail_description=kitchen.thumbnail_description,
        list_images=BaseCollectionListImageRecord.from_model(model=kitchen),
    )


def kitchen_available_list() -> list[KitchenRecord]:
    """
    Returns a list of active kitchens.
    """

    kitchens = Kitchen.objects.available().select_related("supplier").order_by("-id")

    return [kitchen_record(kitchen=kitchen) for kitchen in kitchens]


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

    kitchen_base_record = kitchen_record(kitchen=kitchen)

    record = KitchenDetailRecord(
        **kitchen_base_record.dict(),
        description=kitchen.description,
        extra_description=kitchen.extra_description,
        example_from_price=kitchen.example_from_price,
        can_be_painted=kitchen.can_be_painted,
        silk_variants=[
            KitchenVariantColorRecord(id=obj.id, name=obj.name, color_hex=obj.color_hex)
            for obj in kitchen.silk_variants.all()
        ],
        decor_variants=[
            KitchenVariantRecord(
                id=obj.id,
                name=obj.name,
                image_url=obj.image_url,
                image80x80_url=obj.image80x80_url,
                image380x575_url=obj.image380x575_url,
            )
            for obj in kitchen.decor_variants.all()
        ],
        plywood_variants=[
            KitchenVariantRecord(
                id=obj.id,
                name=obj.name,
                image_url=obj.image_url,
                image80x80_url=obj.image80x80_url,
                image380x575_url=obj.image380x575_url,
            )
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
        images=BaseHeaderImageRecord.from_model(model=kitchen),
    )

    return record
