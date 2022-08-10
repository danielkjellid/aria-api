from django.db.models import Prefetch

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

    prefetch_options = Prefetch(
        "product_options",
        queryset=ProductOption.objects.available()
        .select_related("product", "product__supplier")
        .prefetch_related("product__colors", "product__shapes", "product__options"),
        to_attr="available_options",
    )

    prefetch_products = Prefetch(
        "products",
        queryset=Product.objects.available().preload_for_list(),
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

        for product in discount_product.available_products:
            aggregated_products.add(product)

        for option in discount_product.available_options:
            aggregated_products.add(option.product)

        records.append(
            DiscountRecord(
                id=discount_product.id,
                name=discount_product.name,
                description=discount_product.description
                if discount_product.description
                else None,
                slug=discount_product.slug if discount_product.slug else None,
                products=[
                    ProductListRecord(
                        id=product.id,
                        name=product.name,
                        slug=product.slug,
                        supplier=ProductSupplierRecord(
                            id=product.supplier.id,
                            name=product.supplier.name,
                            origin_country=product.supplier.origin_country.name,
                            origin_country_flag=product.supplier.origin_country.unicode_flag,
                        ),
                        thumbnail=product.thumbnail.url if product.thumbnail else None,
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
                    for product in aggregated_products
                ],
                minimum_quantity=discount_product.minimum_quantity
                if discount_product.minimum_quantity
                else None,
                maximum_quantity=discount_product.maximum_quantity
                if discount_product.maximum_quantity
                else None,
                discount_gross_pr=discount_product.discount_gross_price
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
