from datetime import datetime
from decimal import Decimal

from django.utils.text import slugify

from aria.discounts.models import Discount
from aria.products.models import Product, ProductOption


def create_discount(
    *,
    name: str = "Test discount",
    description: str | None = None,
    slug: str | None = None,
    products: list[Product] | None = None,
    product_options: list[ProductOption] | None = None,
    minimum_quantity: int | None = None,
    maximum_quantity: int | None = None,
    discount_gross_price: Decimal | None = None,
    discount_gross_percentage: Decimal | None = None,
    maximum_sold_quantity: int | None = None,
    total_sold_quantity: int | None = None,
    active_at: datetime | None = None,
    active_to: datetime | None = None,
    ordering: int | None = None,
) -> Discount:
    """
    Create a discount for products and/or product options used for testing
    purposes.
    """

    if not slug:
        slug = slugify(name)

    if not discount_gross_percentage and not discount_gross_price:
        raise Exception(
            "Discount must either discount a gross percentage or set price."
        )

    discount = Discount.objects.create(
        name=name,
        description=description,
        slug=slug,
        minimum_quantity=minimum_quantity,
        maximum_quantity=maximum_quantity,
        discount_gross_price=discount_gross_price,
        discount_gross_percentage=discount_gross_percentage,
        maximum_sold_quantity=maximum_sold_quantity,
        total_sold_quantity=total_sold_quantity,
        active_at=active_at,
        active_to=active_to,
        ordering=ordering,
    )

    if products:
        discount.products.set(products)

    if product_options:
        discount.product_options.set(product_options)

    discount.save()

    return discount
