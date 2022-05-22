from aria.categories.models import Category
from aria.categories.schemas.records import CategoryDetailRecord, CategoryRecord
from aria.core.selectors import base_header_image_record
from aria.products.models import Product


def categories_navigation_active_list() -> list[CategoryDetailRecord]:
    """
    Returns a queryset of active navigation categories.
    """

    categories = Category.objects.primary_and_secondary().active().get_cached_trees()

    return [category_detail_record(category=category) for category in categories]


def categories_parent_active_list() -> list[CategoryRecord]:
    """
    Returns a queryset of active first level categories (is_primary)
    """

    categories = Category.objects.primary().active().get_cached_trees()

    return [category_record(category=category) for category in categories]


def categories_parents_active_list_for_category(
    category: Category,
) -> list[CategoryRecord]:
    """
    Get a list of active parents for a single category instance.
    """

    parents = category.get_ancestors().active().get_cached_trees()

    return [category_record(category=parent) for parent in parents]


def categories_children_active_list_for_category(
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
    )


def category_detail_record(*, category: Category) -> CategoryDetailRecord:
    """
    Get the detail record representation for a single category instance.
    """

    parents = categories_parents_active_list_for_category(category=category)
    children = categories_children_active_list_for_category(category=category)

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
    )
