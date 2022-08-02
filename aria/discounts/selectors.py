from django.db.models import F, Q
from django.utils import timezone

from aria.discounts.models import DiscountProduct
from aria.discounts.records import DiscountProductRecord
from aria.products.enums import ProductStatus
from aria.products.selectors import product_record


def discount_product_record(discount_product: DiscountProduct) -> DiscountProductRecord:
    """
    Get the record representation for a single discount product instance.
    """

    prefetched_products = getattr(discount_product, "discounted_products", None)

    if prefetched_products is not None:
        products = prefetched_products
    else:
        products = discount_product.products.filter(status=ProductStatus.AVAILABLE)

    return DiscountProductRecord(
        id=discount_product.id,
        name=discount_product.name,
        description=discount_product.description
        if discount_product.description
        else None,
        slug=discount_product.slug if discount_product.slug else None,
        products=[product_record(product=product) for product in products],
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


def discounted_products_active_list() -> list[DiscountProductRecord]:

    datetime_now = timezone.now()

    discount_products = DiscountProduct.objects.filter(
        # Discounts can optionally have a start and/or end time set.
        Q(active_at__isnull=True) | Q(active_at__lte=datetime_now),
        Q(active_to__isnull=True) | Q(active_to__gte=datetime_now),
        # If the discount has a maximum sold quantity set, filter out those
        # discounts that have passed the limit.
        Q(maximum_sold_quantity__isnull=True)
        | Q(maximum_sold_quantity__gt=F("total_sold_quantity")),
    ).with_products()

    return [
        discount_product_record(discount_product=discount_product)
        for discount_product in discount_products
    ]
