from django.db.models import Prefetch

from aria.categories.models import Category
from aria.categories.schemas.records import (
    CategoryDetailRecord,
    CategoryProductColorRecord,
    CategoryProductRecord,
    CategoryProductShapeRecord,
    CategoryProductSupplierRecord,
    CategoryProductVariantRecord,
    CategoryRecord,
)
from aria.core.decorators import cached
from aria.core.selectors import base_header_image_record, base_list_image_record
from aria.products.enums import ProductUnit
from aria.products.filters import ProductSearchFilter
from aria.products.models import Product, ProductOption


def category_record(*, category: Category) -> CategoryRecord:
    """
    Get the record representation for a single category instance.
    """

    return CategoryRecord(
        id=category.id,
        name=category.name,
        slug=category.slug,
        description=category.description,
        ordering=category.ordering,
        parent=category.parent_id,
        images=base_header_image_record(instance=category),
        list_images=base_list_image_record(instance=category),
    )


def category_detail_record(*, category: Category) -> CategoryDetailRecord:
    """
    Get the detail record representation for a single category instance.
    """

    parents = category_parents_active_list_for_category(category=category)
    children = category_children_active_list_for_category(category=category)

    return CategoryDetailRecord(
        id=category.id,
        name=category.name,
        ordering=category.ordering,
        slug=category.slug,
        description=category.description,
        parent=category.parent_id,
        parents=parents,
        children=children,
        images=base_header_image_record(instance=category),
        list_images=base_list_image_record(instance=category),
    )


def category_navigation_active_list() -> list[CategoryDetailRecord]:
    """
    Returns a list of active navigation categories.
    """

    categories = Category.objects.primary_and_secondary().active().get_cached_trees()

    return [category_detail_record(category=category) for category in categories]


def category_parent_active_list() -> list[CategoryRecord]:
    """
    Returns a list of active first level categories (is_primary)
    """

    categories = Category.objects.primary().active().get_cached_trees()

    return [category_record(category=category) for category in categories]


def category_parents_active_list_for_category(
    category: Category,
) -> list[CategoryRecord]:
    """
    Get a list of active parents for a single category instance.
    """

    parents = category.get_ancestors().active().get_cached_trees()

    return [category_record(category=parent) for parent in parents]


def category_children_active_list_for_category(
    category: Category,
) -> list[CategoryRecord]:
    """
    Returns a list of active second level categories (is_secondary).
    """

    # Check if cached children exist. If not cached, filter
    # children to get active, as it gets all children by default.
    if hasattr(category, "_cached_children"):
        children = category.get_children().order_by("ordering")
    else:
        children = category.get_children().active().order_by("ordering")

    return [category_record(category=child) for child in children]


def category_tree_active_list_for_product(*, product: Product) -> CategoryDetailRecord:
    """
    Get a full represenation of a nested category tree connected to
    a single product instance.

    If possible, use the manager method with_active_categories()
    on the product queryset before sending in the product instance
    arg.
    """

    # Attempt to get prefetched categories if they exist.
    prefetched_active_categories = getattr(product, "active_categories", None)

    if prefetched_active_categories is not None:
        active_categories = prefetched_active_categories
    else:
        # If prefetched value does not exist, fall back to a queryset.
        active_categories = product.categories.active().order_by("-mptt_level")

    return [category_detail_record(category=category) for category in active_categories]


def category_related_product_list_by_category(
    *, category: Category, filters=None
) -> list[CategoryProductRecord]:
    """
    Returns a filterable list of products belonging to the given category
    slug.
    """

    filters = filters or {}

    # Preload all needed values
    qs = (
        Product.objects.by_category(category)
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
        CategoryProductRecord(
            id=product.id,
            name=product.name,
            slug=product.slug,
            unit=ProductUnit(product.unit).label,
            supplier=CategoryProductSupplierRecord(
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
                CategoryProductColorRecord(
                    id=color.id, name=color.name, color_hex=color.color_hex
                )
                for color in product.colors.all()
            ],
            shapes=[
                CategoryProductShapeRecord(
                    id=shape.id, name=shape.name, image=shape.image.url
                )
                for shape in product.shapes.all()
            ],
            variants=[
                CategoryProductVariantRecord(
                    id=option.variant.id,
                    name=option.variant.name,
                    image=option.variant.image.url if option.variant.image else None,
                    thumbnail=option.variant.thumbnail.url
                    if option.variant.thumbnail
                    else None,
                )
                for option in product.options.all()
                if option.variant
            ],
        )
        for product in filtered_qs
    ]


def _category_related_product_list_cache_key(*, category: Category, filters=None):
    return f"categories.category_id={category.id}.products.filters={filters}"


@cached(key=_category_related_product_list_cache_key, timeout=5 * 60)
def category_related_product_list_by_category_from_cache(
    *, category: Category, filters=None
) -> list[CategoryProductRecord]:
    """
    Returns a filterable list of products belonging to the given category
    slug from cache.
    """

    return category_related_product_list_by_category(category=category, filters=filters)
