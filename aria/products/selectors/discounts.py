import itertools
from decimal import ROUND_HALF_UP, Decimal

from django.db.models import Prefetch

from aria.discounts.models import Discount
from aria.products.models import Product, ProductOption
from aria.products.records import ProductDiscountRecord
from aria.products.selectors.pricing import product_get_price_from_options


def _calculate_discounted_price(*, price: Decimal, discount: Discount) -> Decimal:
    """
    Calculate a discounted price.

    Will set the price to a discount's discount_gross_price, or
    calculate price based on discount percentage if that is defined
    instead.
    """

    if discount.discount_gross_price:
        discounted_gross_price = discount.discount_gross_price
    elif discount.discount_gross_percentage:
        discounted_gross_price = Decimal(price) * (
            Decimal("1") - discount.discount_gross_percentage
        )

    discounted_gross_price = discounted_gross_price.quantize(
        Decimal(".01"), rounding=ROUND_HALF_UP
    )

    return discounted_gross_price


def product_calculate_discounted_price(
    *, product: Product, discount: Discount
) -> Decimal:
    """
    Get discounted price for a product.
    """

    return _calculate_discounted_price(
        price=product_get_price_from_options(product=product), discount=discount
    )


def product_option_calculate_discounted_price(
    *, option: ProductOption, discount: Discount
) -> Decimal:
    """
    Get discounted price for an option.
    """

    return _calculate_discounted_price(price=option.gross_price, discount=discount)


def product_get_active_discount(*, product: Product) -> ProductDiscountRecord | None:
    """
    Get an active discount for a specific product. A discount can either be
    on the product level, or it can be for a specific option. This selector
    will combine them.

    This means that if there is a discount for a single option related to a
    product, this selector will "catch" it, and append it.

    If used in a loop, it's preferable to use it alongside the
    .preload_for_list() queryset manager method.
    """

    prefetched_active_product_discounts = getattr(product, "active_discounts", None)
    prefetched_active_options_discounts = getattr(
        product, "available_options_with_discounts", None
    )

    active_discounts = []

    # Use prefetched attributes if available.
    if prefetched_active_product_discounts is not None:
        active_discounts = prefetched_active_product_discounts

    if prefetched_active_options_discounts is not None and len(active_discounts) == 0:
        active_options_discounts = []

        if len(prefetched_active_options_discounts) > 0:
            # Extract a list of discounts associated with the options.
            active_options_discounts = list(
                itertools.chain(
                    *[
                        option.active_discounts
                        for option in prefetched_active_options_discounts
                        if len(option.active_discounts) > 0
                    ]
                )
            )

        active_discounts = active_discounts + active_options_discounts

    # Fall back to retrieving data from queryset if prefetched attributes
    # isn't available.
    if (
        prefetched_active_product_discounts is None
        and prefetched_active_options_discounts is None
    ):
        product_discounts = list(product.discounts.active())
        options_discounts = []

        options = product.options.available().prefetch_related(
            Prefetch(
                "discounts",
                queryset=Discount.objects.active(),
                to_attr="active_discounts",
            )
        )

        if len(options) > 0:
            # Extract a list over discounts associated with the options.
            options_discounts = list(
                itertools.chain(
                    *[
                        option.active_discounts  # type: ignore
                        for option in options
                        if len(option.active_discounts) > 0  # type: ignore
                    ]
                )
            )

        active_discounts = product_discounts + options_discounts

    if len(active_discounts) == 0:
        return None

    discount = active_discounts[0]

    return ProductDiscountRecord(
        is_discounted=True,
        discounted_gross_price=product_calculate_discounted_price(
            product=product, discount=discount
        ),
        discounted_gross_percentage=discount.discount_gross_percentage
        if discount.discount_gross_percentage
        else None,
        maximum_sold_quantity=discount.maximum_sold_quantity
        if discount.maximum_sold_quantity
        else None,
        remaining_quantity=(
            discount.maximum_sold_quantity - discount.total_sold_quantity
        )
        if discount.maximum_sold_quantity and discount.total_sold_quantity
        else None,
    )


def product_option_get_active_discount(
    *, product_option: ProductOption
) -> ProductDiscountRecord | None:
    """
    Get an active discount for a specific option. A discount can either be
    on the product level, or it can be for a specific option. This selector
    will combine them.

    This means that if there is a discount for a product, all related options
    will inherit that discount and append it, unless there is specified a more
    specific discount on the option itself.
    """

    prefetched_active_product_discounts = getattr(
        product_option.product, "active_discounts", None
    )
    prefetched_active_options_discounts = getattr(
        product_option, "active_discounts", None
    )

    active_discounts = []

    # Attempt to find discounts through prefetched attributes first.
    if prefetched_active_options_discounts is not None:
        active_discounts = prefetched_active_options_discounts

    if prefetched_active_product_discounts is not None and len(active_discounts) == 0:
        active_discounts = prefetched_active_product_discounts

    # Fall back to retrieving data from queryset if prefetched attributes
    # isn't available.
    if (
        prefetched_active_product_discounts is None
        and prefetched_active_options_discounts is None
    ):
        active_options_discounts = list(product_option.discounts.active())
        active_product_discounts = list(product_option.product.discounts.active())

        active_discounts = active_options_discounts + active_product_discounts

    if len(active_discounts) == 0:
        return None

    discount = active_discounts[0]

    return ProductDiscountRecord(
        is_discounted=True,
        discounted_gross_price=product_option_calculate_discounted_price(
            option=product_option, discount=discount
        ),
        discounted_gross_percentage=discount.discount_gross_percentage
        if discount.discount_gross_percentage
        else None,
        maximum_sold_quantity=discount.maximum_sold_quantity
        if discount.maximum_sold_quantity
        else None,
        remaining_quantity=(
            discount.maximum_sold_quantity - discount.total_sold_quantity
        )
        if discount.maximum_sold_quantity and discount.total_sold_quantity
        else None,
    )
