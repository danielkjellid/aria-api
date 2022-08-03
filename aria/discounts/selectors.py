from aria.discounts.models import Discount
from aria.discounts.records import DiscountRecord
from aria.products.records import ProductListRecord
from aria.products.selectors import product_list_for_qs


def discount_record(discount_product: Discount) -> DiscountRecord:
    """
    Get the record representation for a single discount product instance.
    """

    return DiscountRecord(
        id=discount_product.id,
        name=discount_product.name,
        description=discount_product.description
        if discount_product.description
        else None,
        slug=discount_product.slug if discount_product.slug else None,
        products=product_list_for_qs(
            products=discount_product.products.all(), filters=None
        ),
        minimum_quantity=discount_product.minimum_quantity
        if discount_product.minimum_quantity
        else None,
        maximum_quantity=discount_product.maximum_quantity
        if discount_product.maximum_quantity
        else None,
        discount_gross_price=discount_product.discount_gross_price
        if discount_product.discount_gross_price
        else None,
        discount_gross_percentage=discount_product.discount_gross_percentage
        if discount_product.discount_gross_percentage
        else None,
        maximum_sold_quantity=discount_product.maximum_sold_quantity
        if discount_product.maximum_sold_quantity
        else None,
        total_sold_quantity=discount_product.total_sold_quantity
        if discount_product.total_sold_quantity
        else None,
        display_maximum_quantity=discount_product.display_maximum_quantity,
        active_at=discount_product.active_at if discount_product.active_to else None,
        active_to=discount_product.active_to if discount_product.active_to else None,
        ordering=discount_product.ordering if discount_product.ordering else None,
    )


def discount_active_list() -> list[ProductListRecord]:
    """
    Get a list of currently active discounts.
    """

    discount_products = Discount.objects.active()

    return [
        discount_record(discount_product=discount_product)
        for discount_product in discount_products
    ]
