from decimal import ROUND_HALF_UP, Decimal
from typing import TypedDict

from django.db import transaction
from django.utils.translation import gettext as _

from aria.core.exceptions import ApplicationError
from aria.products.enums import ProductStatus
from aria.products.models import Product, ProductOption, Size, Variant
from aria.products.records import ProductOptionRecord
from aria.products.services.sizes import size_bulk_create, size_clean_and_validate_value


def product_option_create(
    *,
    product: Product,
    gross_price: Decimal | float,
    status: ProductStatus = ProductStatus.AVAILABLE,
    size: Size | None = None,
    variant: Variant | None = None,
) -> ProductOptionRecord:

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
        status=product_option.status,
        variant_id=product_option.variant_id,
        size_id=product_option.size_id,
    )


class ProductOptionDict(TypedDict):
    gross_price: Decimal
    status: ProductStatus
    size_id: int
    variant_id: int


@transaction.atomic
def product_option_bulk_create(
    *, product_id: int, product_options: list[ProductOptionDict]
) -> list[ProductOptionRecord]:

    if product_id is None:
        raise ValueError("Product must be defined.")

    if product_id is None:
        raise ValueError("Product must be defined.")

    if any(
        option.get("size_id", None) is None and option.get("variant_id", None) is None
        for option in product_options
    ):
        raise ValueError("Either size or variant must be defined")

    product_options_to_create = [
        ProductOption(
            product_id=product_id,
            status=option["status"],
            gross_price=option["gross_price"],
            size_id=option["size_id"],
            variant_id=option["variant_id"],
        )
        for option in product_options
    ]

    options_created = ProductOption.objects.bulk_create(product_options_to_create)

    return [
        ProductOptionRecord(
            id=option.id,
            gross_price=option.gross_price,
            status=option.status_display,
            variant_id=option.variant_id,
            size_id=option.size_id,
        )
        for option in options_created
    ]


class OptionSizeDict(TypedDict):
    width: float | None
    height: float | None
    depth: float | None
    circumference: float


class ProductOptionSizeDict(TypedDict):
    status: int
    gross_price: float
    variant_id: int | None
    size: OptionSizeDict | None


@transaction.atomic
def product_option_bulk_create_option_and_sizes(
    *, product_id: int, options: list[ProductOptionSizeDict]
) -> list[ProductOptionRecord]:

    copied_options = options.copy()
    copied_options = [
        options["size"] for option in copied_options if option is not None
    ]

    for option in copied_options:
        if option.get("size", None) is not None:
            width = option.get("size", {}).get("width")
            height = option.get("size", {}).get("height")
            depth = option.get("size", {}).get("depth")
            circumference = option.get("size", {}).get("circumference")

            option["size"] = size_clean_and_validate_value(
                width=width, height=height, depth=depth, circumference=circumference
            )

    sizes_from_options = [
        {
            "width": option.get("size", {}).get("width"),
            "height": option.get("size", {}).get("height"),
            "depth": option.get("size", {}).get("depth"),
            "circumference": option.get("size", {}).get("circumference"),
        }
        for option in copied_options
    ]

    sizes = size_bulk_create(sizes=sizes_from_options)

    options_to_create = [
        {
            "status": option.status,
            "gross_price": option.gross_price,
            "variant_id": option.variant_id,
            "size_id": next(
                size.id
                for size in sizes
                if option.size.width == size.width
                and option.size.height == size.height
                and option.size.depth == size.depth
                and option.size.circumference == size.circumference
            ),
        }
        for option in copied_options
    ]

    created_options = product_option_bulk_create(
        product_id=product_id, product_options=options_to_create
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
        and len(related_variant.product_options.all()) == 1
    ):
        related_variant.delete()
