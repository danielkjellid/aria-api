from django.db.models import Prefetch

from aria.discounts.models import Discount
from aria.product_attributes.records import SizeDetailRecord, VariantDetailRecord
from aria.products.enums import ProductStatus
from aria.products.models import Product
from aria.products.records import ProductOptionDetailRecord
from aria.products.selectors.discounts import product_option_get_active_discount


def product_options_list_for_product(
    *, product: Product
) -> list[ProductOptionDetailRecord]:
    """
    Get a full representation of a product options connected to a single product
    instance.

    If possible, use the manager method with_available_options_and_options_discounts()
    on the product queryset before sending in the product instance arg.
    """

    # Attempt to get prefetched product options if they exist.
    prefetched_product_options = getattr(product, "available_options", None)

    if prefetched_product_options is not None:
        options = prefetched_product_options
    else:
        # If prefetched value does not exist, fall back to a queryset.
        options = (
            product.options.filter(status=ProductStatus.AVAILABLE)
            .select_related(
                "variant",
                "size",
            )
            .prefetch_related(
                Prefetch(
                    "discounts",
                    queryset=Discount.objects.active(),
                    to_attr="active_discounts",
                )
            )
        )

    return [
        ProductOptionDetailRecord(
            id=option.id,
            discount=product_option_get_active_discount(product_option=option),
            gross_price=option.gross_price,
            status=option.status_display,
            variant=VariantDetailRecord(
                id=option.variant.id,
                name=option.variant.name,
                image_url=option.variant.image.url if option.variant.image else None,
                thumbnail_url=option.variant.thumbnail.url
                if option.variant.thumbnail
                else None,
                is_standard=option.variant.is_standard,
            )
            if option.variant
            else None,
            size=SizeDetailRecord(
                id=option.size.id,
                width=option.size.width,
                height=option.size.height,
                depth=option.size.depth,
                circumference=option.size.circumference,
                name=option.size.name,
            )
            if option.size
            else None,
        )
        for option in options
    ]
