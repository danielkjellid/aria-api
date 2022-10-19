from typing import Any

from django.db.models import Q

from aria.categories.models import Category
from aria.categories.selectors import category_tree_active_list_for_product
from aria.core.decorators import cached
from aria.core.models import BaseQuerySet
from aria.core.selectors import base_header_image_record
from aria.products.filters import ProductSearchFilter
from aria.products.models import Product
from aria.products.records import (
    ProductColorRecord,
    ProductDetailRecord,
    ProductFileRecord,
    ProductListRecord,
    ProductShapeRecord,
)
from aria.products.schemas.filters import ProductListFilters
from aria.products.selectors.pricing import product_get_price_from_options
from aria.products.selectors.product_options import product_options_list_for_product
from aria.products.selectors.records import product_list_record, product_record


def product_detail(
    *, product_id: int | None = None, product_slug: str | None = None
) -> ProductDetailRecord | None:
    """
    Get the detailed representation of a single product based on either
    id or slug, although one of them has to be provided.

    Be careful to not run this in a loop unless absolutely needed. It
    already does quite a few queries, and will to that amount per loop
    iteration.
    """

    product = (
        Product.objects.filter(Q(id=product_id) | Q(slug=product_slug))  # type: ignore
        .with_active_categories()
        .with_colors()
        .with_shapes()
        .with_files()
        .with_available_options_and_option_discounts()
        .with_active_product_discounts()
        .annotate_from_price()
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
        from_price=product_get_price_from_options(product=product),
        display_price=product.display_price,
        can_be_picked_up=product.can_be_picked_up,
        can_be_purchased_online=product.can_be_purchased_online,
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


def product_list_for_sale_for_qs(
    *,
    products: BaseQuerySet["Product"] | None,
    filters: ProductListFilters | dict[str, Any] | None,
) -> list[ProductListRecord]:
    """
    Returns a filterable list of products based on given queryset. The
    ProductListRecord is a record of mutual properties for use whenever we
    show a list of products frontend.
    """

    filters = filters or {}

    if products is not None:
        qs = products.preload_for_list().order_by("-created_at")  # type: ignore

    else:
        qs = Product.objects.available().preload_for_list().order_by("-created_at")  # type: ignore # pylint: disable=line-too-long

    filtered_qs = ProductSearchFilter(filters, qs).qs

    return [product_list_record(product=product) for product in filtered_qs]


def product_list(
    *, filters: ProductListFilters | dict[str, Any] | None
) -> list[ProductListRecord]:
    """
    Returns a filterable list of products.
    """

    products = Product.objects.all()

    return product_list_for_sale_for_qs(products=products, filters=filters)


def product_list_for_sale(
    *, filters: ProductListFilters | dict[str, Any] | None
) -> list[ProductListRecord]:
    """
    Returns a filterable list of products for sale.
    """

    products = Product.objects.available()

    return product_list_for_sale_for_qs(products=products, filters=filters)


def _product_list_for_sale_cache_key(
    *, filters: ProductListFilters | dict[str, Any] | None
) -> str:
    return f"products.for_sale.filters={filters}"


@cached(key=_product_list_for_sale_cache_key, timeout=5 * 60)
def product_list_for_sale_from_cache(
    *, filters: ProductListFilters | dict[str, Any] | None
) -> list[ProductListRecord]:
    """
    Returns a filterable list of products for sale from cache.
    """

    return product_list_for_sale(filters=filters)


def product_list_by_category(
    *, category: Category, filters: ProductListFilters | dict[str, Any] | None
) -> list[ProductListRecord]:
    """
    Returns a filterable list of products belonging to the given category.
    """

    products_by_category = Product.objects.by_category(category)

    return product_list_for_sale_for_qs(products=products_by_category, filters=filters)


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
