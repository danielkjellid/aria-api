from typing import TypedDict

from django.db.models import Prefetch

from aria.core.decorators import cached
from aria.discounts.models import Discount
from aria.discounts.records import DiscountRecord
from aria.products.models import Product, ProductOption
from aria.products.records import (
    ProductColorRecord,
    ProductDiscountRecord,
    ProductListRecord,
    ProductShapeRecord,
    ProductSupplierRecord,
    ProductVariantRecord,
)
from aria.products.selectors import (
    product_calculate_discounted_price_for_product,
    product_get_price_from_options,
    product_list_for_sale_for_qs,
)


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
        products=product_list_for_sale_for_qs(
            products=discount_product.products.available(), filters=None  # type: ignore
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


class DiscountDataDict(TypedDict):
    discount_id: int
    products: set[int]


def discount_active_list() -> list[DiscountRecord]:
    """
    Get a list of currently active discounts.
    """

    discounts = (
        Discount.objects.active()
        .prefetch_related(
            Prefetch(
                "product_options",
                queryset=(ProductOption.objects.available().select_related("product")),
                to_attr="available_options",
            ),
            Prefetch(
                "products",
                queryset=Product.objects.available(),
                to_attr="available_products",
            ),
        )
        .order_by("ordering")
    )

    discount_data: list[DiscountDataDict] = []

    # Because of how you can have a discount on both products and product
    # options, and we essentially want to initially show the discount on
    # the product itself (even though only one option might be discounted)
    # we need to loop over each discount and flatten products + option
    # products.
    for discount in discounts:
        aggregated_product_ids: set[int] = set()

        for product in discount.available_products:  # type: ignore
            aggregated_product_ids.add(product.id)

        for option in discount.available_options:  # type: ignore
            aggregated_product_ids.add(option.product.id)

        # Add data with which product ids is associated with each discount.
        discount_data.append(
            {"discount_id": discount.id, "products": aggregated_product_ids}
        )

    # Retrieve all products id's for all discounts (flatten products values
    # in discount_data).
    flattened_aggregated_products = [
        val for d in discount_data for val in d["products"]
    ]

    # Refetch all products, + products from options prefetching it with needed
    # list values.
    products = (
        Product.objects.available()  # type: ignore
        .filter(id__in=flattened_aggregated_products)
        .preload_for_list()
        .order_by("-created_at")
    )

    def _find_products_in_discount_data(discount_id: int) -> list[Product]:
        """
        Helper method for finding associated products based on discount.
        """
        for d in discount_data:
            if d["discount_id"] == discount_id:
                return [
                    product
                    for product in products
                    for product_id in d["products"]
                    if product_id == product.id
                ]
        return []

    return [
        DiscountRecord(
            id=discount.id,
            name=discount.name,
            description=discount.description if discount.description else None,
            slug=discount.slug,
            products=[
                ProductListRecord(
                    id=product.id,
                    name=product.name,
                    slug=product.slug,
                    unit=product.unit_display,
                    supplier=ProductSupplierRecord(
                        id=product.supplier.id,
                        name=product.supplier.name,
                        origin_country=product.supplier.origin_country.name,
                        origin_country_flag=product.supplier.origin_country.unicode_flag,  # pylint: disable=line-too-long
                    ),
                    thumbnail=product.thumbnail.url if product.thumbnail else None,
                    display_price=product.display_price,
                    from_price=product_get_price_from_options(product=product),
                    discount=ProductDiscountRecord(
                        is_discounted=True,
                        discounted_gross_price=product_calculate_discounted_price_for_product(  # pylint: disable=line-too-long
                            product=product, discount=discount
                        ),
                        maximum_sold_quantity=discount.maximum_sold_quantity
                        if discount.maximum_sold_quantity
                        else None,
                        remaining_quantity=(
                            discount.maximum_sold_quantity
                            - discount.total_sold_quantity
                        )
                        if discount.maximum_sold_quantity
                        and discount.total_sold_quantity
                        else None,
                    ),
                    materials=product.materials_display,
                    rooms=product.rooms_display,
                    colors=[
                        ProductColorRecord(
                            id=color.id, name=color.name, color_hex=color.color_hex
                        )
                        for color in product.colors.all()
                    ],
                    shapes=[
                        ProductShapeRecord(
                            id=shape.id, name=shape.name, image=shape.image.url
                        )
                        for shape in product.shapes.all()
                    ],
                    variants=[
                        ProductVariantRecord(
                            id=option.variant.id,
                            name=option.variant.name,
                            image=option.variant.image.url
                            if option.variant.image
                            else None,
                            thumbnail=option.variant.thumbnail.url
                            if option.variant.thumbnail
                            else None,
                            is_standard=option.variant.is_standard,
                        )
                        for option in product.available_options_unique_variants  # type: ignore # pylint: disable=line-too-long
                        if option.variant
                    ],
                )
                for product in _find_products_in_discount_data(discount_id=discount.id)
                if len(_find_products_in_discount_data(discount_id=discount.id)) > 0
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
