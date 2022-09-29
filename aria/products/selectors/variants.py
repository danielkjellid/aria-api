from aria.products.models import Variant
from aria.products.records import ProductVariantRecord


def variant_list() -> list[ProductVariantRecord]:
    """
    Returns a list of all variants in the application.
    """

    variants = Variant.objects.all().order_by("-id")

    return [
        ProductVariantRecord(
            id=variant.id,
            name=variant.name,
            is_standard=variant.is_standard,
            image=variant.image.url if variant.image else None,
            thumbnail=variant.thumbnail.url if variant.thumbnail else None,
        )
        for variant in variants
    ]
