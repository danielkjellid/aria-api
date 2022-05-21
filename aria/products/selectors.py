from django.db.models import Q

from aria.categories.models import Category
from aria.products.enums import ProductStatus
from aria.products.filters import ProductSearchFilter
from aria.products.models import Product
from aria.core.schemas.records import BaseHeaderImageRecord
from aria.products.schemas.records import (
    ProductRecord,
    ProductDetailRecord,
    ProductSupplierRecord,
    ProductShapeRecord,
    ProductFileRecord,
    ProductOptionRecord,
    ProductSizeRecord,
    ProductVariantRecord,
    ProductColorRecord,
)
from aria.categories.selectors import category_tree_active_list_for_product


def product_list_by_category(
    *, filters=None, category: Category
) -> list[ProductRecord]:
    """
    Returns a list of products bellonging to the given
    category parent slug.
    """

    filters = filters or {}

    qs = category.get_products().filter(status=ProductStatus.AVAILABLE)
    filtered_qs = ProductSearchFilter(filters, qs).qs

    return [product_record(product=product) for product in filtered_qs]


def product_options_list_for_product(product: Product) -> list[ProductOptionRecord]:
    """
    Get a full represenation of a product options connected to
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
            status=option.status,
            variant=ProductVariantRecord(
                id=option.variant.id,
                name=option.variant.name,
                image=option.variant.image.url,
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
    id or slug, allthough one of them has to be provided.

    Be careful to not run this in a loop unless absolutely needed. It
    already does quite a few queries, and will to that amount per loop
    iteration.
    """

    product = (
        Product.objects.filter(Q(id=product_id) | Q(slug=product_slug))
        .preload_for_list()
        .with_active_categories()
        .with_available_options()
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
        thumbnail=product.thumbnail.url if product.thumbnail else None,
        images=[
            BaseHeaderImageRecord(
                apply_filter=image.apply_filter,
                image_640x275=image.image_640x275.url if image.image_640x275 else None,
                image_1024x1024=image.image_1024x1024.url
                if image.image_1024x1024
                else None,
                image_512x512=image.image_512x512.url if image.image_512x512 else None,
                image_1024x575=image.image_1024x575.url
                if image.image_1024x575
                else None,
                image_1536x860=image.image_1536x860.url
                if image.image_1536x860
                else None,
                image_2048x1150=image.image_2048x1150.url
                if image.image_2048x1150
                else None,
            )
            for image in product.images.all()
        ],
        options=options,
    )

    return record


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
            origin_country=product.supplier.origin_country,
        ),
        status=product.status,
        slug=product.slug,
        search_keywords=product.search_keywords,
        short_description=product.short_description,
        description=product.description,  # Deprecated
        new_description=product.new_description,
        unit=product.unit,
        vat_rate=product.vat_rate,
        available_in_special_sizes=product.available_in_special_sizes,
        absorption=product.absorption,
        is_imported_from_external_source=product.is_imported_from_external_source,
        materials=product.materials_display,
        rooms=product.rooms_display,
    )
