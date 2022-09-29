from decimal import Decimal

from django.db import transaction

from aria.products.enums import ProductStatus
from aria.products.models import ProductOption, Variant, Product, Size


@transaction.atomic
def product_option_create(
    *,
    product_id: int,
    gross_price: Decimal,
    status: ProductStatus = ProductStatus.AVAILABLE,
    size_id: int | None = None,
    variant_id: int | None = None,
) -> ProductOption:

    if product_id is None:
        raise ValueError("Product must be defined.")

    if size_id is None and variant_id is None:
        raise ValueError("Either size or variant must be defined.")

    product = Product.objects.get(id=product_id)
    variant: Variant | None = None
    size: Size | None = None

    if variant_id:
        variant = Variant.objects.get(id=variant_id)

    if size_id:
        size = Size.objects.get(id=size_id)

    product_option = ProductOption(
        product=product,
        gross_price=gross_price,
        status=status,
        variant=variant,
        size=size,
    )
    product_option.full_clean()
    product_option.save()

    return product_option


def product_option_delete_related_variants(*, instance: ProductOption) -> None:
    """
    Cleanup dangling variants that does not belong to other
    products.
    """

    related_variant: Variant | None = instance.variant

    # Check if there are other products that's linked to the same
    # variant while filtering out standards.
    if (
        related_variant is not None
        and related_variant.is_standard is False
        and len(related_variant.product_options.all()) == 1
    ):
        related_variant.delete()
