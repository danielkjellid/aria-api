from decimal import ROUND_HALF_UP, Decimal
from typing import Any

from django.utils.translation import gettext as _

from aria.core.exceptions import ApplicationError
from aria.products.enums import ProductStatus
from aria.products.models import Product, ProductOption, Size, Variant
from aria.products.records import OptionRecord, ProductOptionRecord
from aria.products.services.sizes import size_bulk_create, size_clean_and_validate_value


def product_option_create(
    *,
    product: Product,
    gross_price: Decimal | float,
    status: ProductStatus = ProductStatus.AVAILABLE,
    size: Size | None = None,
    variant: Variant | None = None,
) -> ProductOptionRecord:
    """
    Create a single product option instance.
    """

    if product is None:
        raise ApplicationError(
            message=_("Product must be defined."),
            extra={"product": _("field required")},
        )

    if size is None and variant is None:
        raise ApplicationError(message=_("Either size or variant must be defined."))

    product_option = ProductOption(
        product=product,
        gross_price=Decimal(gross_price).quantize(
            Decimal(".01"), rounding=ROUND_HALF_UP
        ),
        status=status,
        variant=variant,
        size=size,
    )
    product_option.full_clean()
    product_option.save()

    return ProductOptionRecord(
        id=product_option.id,
        gross_price=product_option.gross_price,
        status=ProductStatus(product_option.status),
        variant_id=product_option.variant_id,
        size_id=product_option.size_id,
    )


def product_option_bulk_create(
    *, product: Product, product_options: list[dict[str, Any]]
) -> list[ProductOptionRecord]:
    """
    Bulk create product options in an effective manner.
    """

    if product is None:
        raise ValueError("Product must be defined.")

    if any(
        option.get("size_id", None) is None and option.get("variant_id", None) is None
        for option in product_options
    ):
        raise ValueError("Either size or variant must be defined")

    product_options_to_create = [
        ProductOption(
            product=product,
            status=option.get("status", ProductStatus.AVAILABLE),
            gross_price=option.get("gross_price", Decimal("0.0")),
            size_id=option.get("size_id", None),
            variant_id=option.get("variant_id", None),
        )
        for option in product_options
    ]

    options_created = ProductOption.objects.bulk_create(product_options_to_create)

    return [
        ProductOptionRecord(
            id=option.id,
            gross_price=option.gross_price,
            status=ProductStatus(option.status),
            variant_id=option.variant_id,
            size_id=option.size_id,
        )
        for option in options_created
    ]


def product_options_bulk_create_options_and_sizes(
    *, product: Product, options: list[OptionRecord]
) -> list[ProductOptionRecord]:
    """
    Bulk create product options and sizes associated with the option that we're missing.
    """

    copied_options = options.copy()

    for option in copied_options:
        if option.size is not None:
            option.size = size_clean_and_validate_value(
                width=option.size.width if option.size.width else None,
                height=option.size.height if option.size.height else None,
                depth=option.size.depth if option.size.depth else None,
                circumference=option.size.circumference
                if option.size.circumference
                else None,
            )

    sizes_from_options = [
        option.size for option in copied_options if option.size is not None
    ]
    sizes = size_bulk_create(sizes=[size.dict() for size in sizes_from_options])  # type: ignore # pylint: disable=line-too-long

    options_to_create = [
        {
            "status": option.status,
            "gross_price": option.gross_price,
            "variant_id": option.variant_id,
            "size_id": next(
                (
                    size.id
                    for size in sizes
                    if option.size is not None
                    and option.size.width == size.width
                    and option.size.height == size.height
                    and option.size.depth == size.depth
                    and option.size.circumference == size.circumference
                ),
                None,
            ),
        }
        for option in copied_options
    ]

    created_options = product_option_bulk_create(
        product=product, product_options=options_to_create
    )

    return created_options


def product_option_delete_related_variants(*, instance: ProductOption) -> None:
    """
    Cleanup dangling variants that does not belong to other
    product options.
    """

    related_variant: Variant | None = instance.variant

    # Check if there are other products that's linked to the same
    # variant while filtering out standards.
    if (
        related_variant is not None
        and related_variant.is_standard is False
        and len(related_variant.product_options.all()) == 1  # type: ignore
    ):
        related_variant.delete()
