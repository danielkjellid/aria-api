from django.core.files import File
from django.utils.text import slugify

from products.models import Variant, Product, ProductOption
from products.enums import ProductStatus
from django.db.models import Model

from products.selectors import get_related_unique_variants


def create_variant(
    *,
    name: str,
    status: int = ProductStatus.DRAFT,
    thumbnail: File = None
) -> Variant:
    """
    Creates a Variant with given fields.
    """

    if not name or not status or not thumbnail:
        raise ValueError(
            'Not all fields necessary present. Got name: %s, status: %s, thumbnail: %s - ',
            name,
            status,
            thumbnail
        )

    new_variant = Variant.objects.create(
        name=name.title(),
        status=status
    )

    # Variants needs an id to save files because the folder structure is
    # <id>-<name>/file, therefore we have to create the variant first,
    # then save the thumbnail file.
    new_variant.thumbnail.save(f'{slugify(new_variant.name)}', thumbnail)

    return new_variant


def delete_related_variants(*, instance: "ProductOption") -> None:
    """
    Cleanup dangling variants that does not belong to other
    products.
    """

    # Get variants related to product option,
    related_variants = Variant.objects.filter(product_options=instance).distinct('pk')

    for variant in related_variants:
        # Check if there are other products thats linked to the same
        # variant.
        variant_products_amount = len(list(variant.product_options.all().distinct('product_id')))

        # If there is, we jump to next loop iteration
        if variant_products_amount != 1:
            continue

        # If not, delete the variant
        variant.delete()
