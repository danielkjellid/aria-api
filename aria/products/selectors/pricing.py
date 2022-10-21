from decimal import Decimal

from django.db.models import Min, Q

from aria.products.models import Product


def product_get_price_from_options(*, product: Product) -> Decimal:
    """
    Get a product's from price based on lowest options price
    available.
    """

    annotated_price = getattr(product, "annotated_from_price", None)

    # If annotated value already exists, return that without taking
    # a roundtrip to the db.
    if annotated_price is not None:
        return Decimal(annotated_price)

    # Aggregate lowest gross price based on a product's options.
    lowest_option_price = product.options.available().aggregate(
        price=Min("gross_price", filter=Q(gross_price__gt=0))
    )["price"]

    return Decimal(lowest_option_price) if lowest_option_price else Decimal("0.00")
