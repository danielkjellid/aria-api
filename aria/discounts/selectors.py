from django.db.models import Prefetch

from aria.core.decorators import cached
from aria.discounts.models import Discount
from aria.discounts.records import DiscountRecord
from aria.products.models import Product, ProductOption
from aria.products.records import (
    ProductColorRecord,
    ProductListRecord,
    ProductShapeRecord,
    ProductSupplierRecord,
    ProductVariantRecord,
)
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
            ProductOption.objects.available()
            .select_related("product", "product__supplier", "variant")
            .distinct("variant_id")
            .prefetch_related(
                "product__colors",
                "product__shapes",
                "product__options",
                "product__options__variant",
            )
        ),
        to_attr="available_options",
    )

    prefetch_products = Prefetch(
        "products",
        queryset=Product.objects.available()
        .select_related("supplier")
        .prefetch_related("colors", "shapes", "options", "options__variant"),
        to_attr="available_products",
    )

    discount_products = (
        Discount.objects.active()
        .prefetch_related(prefetch_options, prefetch_products)
        .order_by("ordering", "created_at")
    )

    records = []

    for discount_product in discount_products:
        aggregated_products = set()

        for product in discount_product.available_products:  # type: ignore
            aggregated_products.add(product)

        for option in discount_product.available_options:  # type: ignore
            aggregated_products.add(option.product)

        records.append(
            DiscountRecord(
                id=discount_product.id,
                name=discount_product.name,
                description=discount_product.description
                if discount_product.description
                else None,
                slug=discount_product.slug,
                products=[
                    ProductListRecord(
                        id=product.id,
                        name=product.name,
                        slug=product.slug,
                        supplier=ProductSupplierRecord(
                            id=product.supplier.id,
                            name=product.supplier.name,
                            origin_country=product.supplier.origin_country.name,
                            origin_country_flag=product.supplier.origin_country.unicode_flag,  # pylint: disable=line-too-long
                        ),
                        thumbnail=product.thumbnail.url if product.thumbnail else None,
                        unit=product.unit_display,
                        display_price=product.display_price,
                        from_price=product.from_price,
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
                            for option in product.options.all()
                            if option.variant
                        ],
                    )
                    for product in sorted(
                        aggregated_products, key=lambda product: product.created_at  # type: ignore # pylint: disable=line-too-long
                    )
                ],
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
                active_at=discount_product.active_at
                if discount_product.active_to
                else None,
                active_to=discount_product.active_to
                if discount_product.active_to
                else None,
                ordering=discount_product.ordering
                if discount_product.ordering
                else None,
            )
        )

    return records


def _discount_active_list_key() -> str:
    return "discounts.active"


@cached(key=_discount_active_list_key, timeout=60 * 2)
def discount_active_list_from_cache() -> list[DiscountRecord]:
    """
    Get a list of currently active discounts from cache.
    """

    return discount_active_list()