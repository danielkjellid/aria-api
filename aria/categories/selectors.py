from typing import Union

from django.db.models import QuerySet

from aria.categories.models import Category
from aria.categories.schemas.records import CategoryDetailRecord, CategoryRecord
from aria.products.models import Product


def categories_navigation_list() -> Union[QuerySet, Category]:
    """
    Returns a queryset of navigation categories.
    """

    return Category.objects.primary_and_secondary().get_cached_trees()


def categories_navigation_active_list() -> list[CategoryDetailRecord]:
    """
    Returns a queryset of active navigation categories.
    """

    categories = Category.objects.primary_and_secondary().active().get_cached_trees()

    return [category_detail_record(category=category) for category in categories]


def categories_parent_active_list() -> Union[QuerySet, Category]:
    """
    Returns a queryset of active first level categories (is_primary)
    """

    return Category.objects.primary().active().get_cached_trees()


def categories_parents_active_list_for_category(
    category: Category,
) -> list[CategoryRecord]:
    """
    Get a list of active parents for a single category instance.
    """

    parents = category.get_ancestors().active().get_cached_trees()

    return [
        CategoryRecord(
            id=parent.id,
            name=parent.name,
            slug=parent.slug,
            ordering=parent.ordering,
            parent=parent.parent_id,
        )
        for parent in parents
    ]


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

    return [
        CategoryRecord(
            id=child.id,
            name=child.name,
            slug=child.slug,
            ordering=child.ordering,
            parent=child.parent_id,
        )
        for child in children
    ]


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


def category_detail_record(*, category: Category) -> CategoryDetailRecord:
    """
    Get the record representation for a single category instance.
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
    )
