from decimal import ROUND_HALF_UP, Decimal
from typing import Any

from django.db.models import Prefetch, Q

from aria.categories.models import Category
from aria.categories.selectors import category_tree_active_list_for_product
from aria.core.decorators import cached
from aria.core.models import BaseQuerySet
from aria.core.selectors import base_header_image_record
from aria.products.enums import ProductStatus, ProductUnit
from aria.products.filters import ProductSearchFilter
from aria.products.models import Product, ProductOption
from aria.products.records import (
    ProductColorRecord,
    ProductDetailRecord,
    ProductDiscountRecord,
    ProductFileRecord,
    ProductListRecord,
    ProductOptionRecord,
    ProductRecord,
    ProductShapeRecord,
    ProductSizeRecord,
    ProductSupplierRecord,
    ProductVariantRecord,
)
from aria.products.schemas.filters import ProductListFilters


def product_record(product: Product) -> ProductRecord:
    """
    Get the record representation for a single product instance.
    """

    return ProductRecord(
        id=product.id,
        name=product.name,
        supplier=ProductSupplierRecord(
            id=product.supplier_id,
            name=product.supplier.name,
            origin_country=product.supplier.origin_country.name,
            origin_country_flag=product.supplier.origin_country.unicode_flag,
        ),
        status=ProductStatus(product.status).label,
        slug=product.slug,
        search_keywords=product.search_keywords,
        short_description=product.short_description,
        description=product.new_description,
        new_description=product.new_description,
        unit=ProductUnit(product.unit).label,
        vat_rate=product.vat_rate,
        available_in_special_sizes=product.available_in_special_sizes,
        absorption=product.absorption,
        is_imported_from_external_source=product.is_imported_from_external_source,
        materials=product.materials_display,
        rooms=product.rooms_display,
        thumbnail=product.thumbnail.url if product.thumbnail else None,
    )


def product_options_list_for_product(product: Product) -> list[ProductOptionRecord]:
    """
    Get a full representation of a product options connected to
    a single product instance.

    If possible, use the manager method with_available_options()
    on the product queryset before sending in the product instance
    arg.
    """

    # Attempt to get prefetched product options if they exist.
    prefetched_product_options = getattr(product, "available_options", None)

    if prefetched_product_options is not None:
        options = prefetched_product_options
    else:
        # If prefetched value does not exist, fall back to a queryset.
        options = product.options.filter(status=ProductStatus.AVAILABLE).select_related(
            "variant", "size"
        )

    return [
        ProductOptionRecord(
            id=option.id,
            gross_price=option.gross_price,
            status=ProductStatus(option.status).label,
            variant=ProductVariantRecord(
                id=option.variant.id,
                name=option.variant.name,
                image=option.variant.image.url if option.variant.image else None,
                thumbnail=option.variant.thumbnail.url
                if option.variant.thumbnail
                else None,
                is_standard=option.variant.is_standard,
            )
            if option.variant
            else None,
            size=ProductSizeRecord(
                id=option.size.id,
                width=option.size.width,
                height=option.size.height,
                depth=option.size.depth,
                circumference=option.size.circumference,
                name=option.size.name,
            )
            if option.size
            else None,
        )
        for option in options
    ]


def product_detail(
    *, product_id: int | None = None, product_slug: str | None = None
) -> ProductDetailRecord | None:
    """
    Get the detailed representation of a single product based on either
    id or slug, although one of them has to be provided.

    Be careful to not run this in a loop unless absolutely needed. It
    already does quite a few queries, and will do that amount per loop
    iteration.
    """

    product = (
        Product.objects.filter(Q(id=product_id) | Q(slug=product_slug))  # type: ignore
        .preload_for_list()
        .with_available_options()
        .annotate_site_state_data()
        .first()
    )

    if not product:
        return None

    categories = category_tree_active_list_for_product(product=product)
    options = product_options_list_for_product(product=product)

    product_base_record = product_record(product=product)

    record = ProductDetailRecord(
        **product_base_record.dict(),
        categories=categories,
        from_price=product.from_price,
        display_price=product.display_price,
        can_be_picked_up=product.can_be_picked_up,
        can_be_purchased_online=product.can_be_purchased_online,
        discount=product_get_discount(product=product),
        colors=[
            ProductColorRecord(id=color.id, name=color.name, color_hex=color.color_hex)
            for color in product.colors.all()
        ],
        shapes=[
            ProductShapeRecord(
                id=shape.id,
                name=shape.name,
                image=shape.image.url if shape.image else None,
            )
            for shape in product.shapes.all()
        ],
        files=[
            ProductFileRecord(
                id=file.id, name=file.name, file=file.file.url if file.file else None
            )
            for file in product.files.all()
        ],
        images=[
            base_header_image_record(instance=image) for image in product.images.all()
        ],
        options=options,
    )

    return record


def product_get_discount(*, product: Product) -> ProductDiscountRecord:

    # As of now, from_price is an annotated value and is crucial for
    # discounts.
    # if not hasattr(product, "from_price"):
    #     return None

    prefetched_active_discounts = getattr(product, "active_discounts", None)

    if prefetched_active_discounts is not None:
        active_discounts = prefetched_active_discounts
    else:
        active_discounts = product.discounts.active()

    if len(active_discounts) == 0:
        return None

    discount = active_discounts[0]

    if discount.discount_gross_price:
        discounted_gross_price = discount.discount_gross_price
    elif discount.discount_gross_percentage:
        discounted_gross_price = Decimal(product.from_price) * (
            Decimal(1) - discount.discount_gross_percentage
        )

    discounted_gross_price = discounted_gross_price.quantize(
        Decimal(".01"), rounding=ROUND_HALF_UP
    )

    return ProductDiscountRecord(
        is_discounted=True,
        discounted_gross_price=discounted_gross_price,
        maximum_sold_quantity=discount.maximum_sold_quantity
        if discount.maximum_sold_quantity
        else None,
        remaining_quantity=(
            discount.maximum_sold_quantity - discount.total_sold_quantity
        ),
    )


def products_for_sale_list_for_qs(
    *,
    products: BaseQuerySet["Product"],
    filters: ProductListFilters | dict[str, Any] | None,
) -> list[ProductListRecord]:
    """
    Returns a filterable list of products based on given queryset. The ProductListRecord is a
    record of mutual properties for use whenever we show a list of products frontend.
    """

    filters = filters or {}

    # Preload all needed values.
    # TODO: include discount data
    qs = (
        products.filter(status=ProductStatus.AVAILABLE)
        .prefetch_related(
            Prefetch(
                "options",
                queryset=ProductOption.objects.select_related("variant").distinct(
                    "variant_id"
                ),
            )
        )
        .preload_for_list()
        .annotate_site_state_data()
    )

    filtered_qs = ProductSearchFilter(filters, qs).qs

    return [
        ProductListRecord(
            id=product.id,
            name=product.name,
            slug=product.slug,
            unit=ProductUnit(product.unit).label,
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
                ProductShapeRecord(id=shape.id, name=shape.name, image=shape.image.url)
                for shape in product.shapes.all()
            ],
            variants=[
                ProductVariantRecord(
                    id=option.variant.id,
                    name=option.variant.name,
                    image=option.variant.image.url if option.variant.image else None,
                    thumbnail=option.variant.thumbnail.url
                    if option.variant.thumbnail
                    else None,
                    is_standard=option.variant.is_standard,
                )
                for option in product.options.all()
                if option.variant
            ],
            discount=product_get_discount(product=product),
        )
        for product in filtered_qs
    ]


def product_list_by_category(
    *, category: Category, filters: ProductListFilters | dict[str, Any] | None
) -> list[ProductListRecord]:
    """
    Returns a filterable list of products belonging to the given category.
    """

    products_by_category = Product.objects.by_category(category)

    return products_for_sale_list_for_qs(products=products_by_category, filters=filters)


def _product_list_by_category_cache_key(
    *, category: Category, filters: ProductListFilters | dict[str, Any] | None
) -> str:
    return f"products.category_id={category.id}.filters={filters}"


@cached(key=_product_list_by_category_cache_key, timeout=5 * 60)
def product_list_by_category_from_cache(
    *, category: Category, filters: ProductListFilters | dict[str, Any] | None
) -> list[ProductListRecord]:
    """
    Returns a filterable list of products belonging to the given category
    from cache.
    """

    return product_list_by_category(category=category, filters=filters)
