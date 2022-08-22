from django.db.models import Prefetch

from aria.core.decorators import cached
from aria.discounts.models import Discount
from aria.discounts.records import DiscountRecord
from aria.products.models import Product, ProductOption
from aria.products.selectors import product_list_for_qs, product_list_record


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
        slug=discount_product.slug,
        products=product_list_for_qs(
            products=discount_product.products.all(), filters=None  # type: ignore
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


def discount_active_list() -> list[DiscountRecord]:
    """
    Get a list of currently active discounts.
    """

    prefetch_options = Prefetch(
        "product_options",
        queryset=(
            # This queryset might look a bit backwords as we're essentially
            # prefetching in reverse order (from product to option), even
            # though the queryset is on option level. This is because in
            # the list view we want to show the _product_, and not the option
            # which makes us do option.product.options.all() to comply with
            # the product list record.
            ProductOption.objects.available().select_related("product")
        ),
        to_attr="available_options",
    )

    prefetch_products = Prefetch(
        "products",
        queryset=Product.objects.available(),
        to_attr="available_products",
    )

    discounts = (
        Discount.objects.active()
        .prefetch_related(prefetch_options, prefetch_products)
        .order_by("ordering", "created_at")
    )

    data = []

    for discount in discounts:

        aggregated_product_ids = set()

        for product in discount.available_products:  # type: ignore
            aggregated_product_ids.add(product.id)

        for option in discount.available_options:  # type: ignore
            aggregated_product_ids.add(option.product.id)

        data.append({"discount_id": discount.id, "products": aggregated_product_ids})

    flattened_aggregated_products = [val for d in data for val in d["products"]]
    products = (
        Product.objects.available()
        .filter(id__in=flattened_aggregated_products)
        .preload_for_list()
        .order_by("-created_at")
    )

    # Find a better way to do this
    def _find_products_in_data(discount_id: int):
        for d in data:
            if d["discount_id"] == discount_id:
                lst = [
                    product
                    for product in products
                    for product_id in d["products"]
                    if product_id == product.id
                ]

                print(
                    [
                        hasattr(product, "available_options_unique_variants")
                        for product in lst
                    ]
                )

                return lst

    return [
        DiscountRecord(
            id=discount.id,
            name=discount.name,
            description=discount.description if discount.description else None,
            slug=discount.slug,
            products=[
                product_list_record(product=product)
                for product in _find_products_in_data(discount_id=discount.id)
            ],
            minimum_quantity=discount.minimum_quantity
            if discount.minimum_quantity
            else None,
            maximum_quantity=discount.maximum_quantity
            if discount.maximum_quantity
            else None,
            discount_gross_price=discount.discount_gross_price
            if discount.discount_gross_price
            else None,
            discount_gross_percentage=discount.discount_gross_percentage
            if discount.discount_gross_percentage
            else None,
            maximum_sold_quantity=discount.maximum_sold_quantity
            if discount.maximum_sold_quantity
            else None,
            total_sold_quantity=discount.total_sold_quantity
            if discount.total_sold_quantity
            else None,
            display_maximum_quantity=discount.display_maximum_quantity,
            active_at=discount.active_at if discount.active_to else None,
            active_to=discount.active_to if discount.active_to else None,
            ordering=discount.ordering if discount.ordering else None,
        )
        for discount in discounts
    ]


def _discount_active_list_key() -> str:
    return "discounts.active"


@cached(key=_discount_active_list_key, timeout=60 * 2)
def discount_active_list_from_cache() -> list[DiscountRecord]:
    """
    Get a list of currently active discounts from cache.
    """

    return discount_active_list()
