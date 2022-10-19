from aria.categories.models import Category
from aria.categories.records import CategoryDetailRecord, CategoryRecord
from aria.core.decorators import cached
from aria.core.selectors import base_header_image_record, base_list_image_record
from aria.products.models import Product


def category_record(*, category: Category) -> CategoryRecord:
    """
    Get the record representation for a single category instance.
    """

    return CategoryRecord(
        id=category.id,
        name=category.name,
        display_name=category.get_category_display(),
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
        display_name=category.get_category_display(),
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


def _category_navigation_active_list_key() -> str:
    return "categories"


def category_children_list() -> list[CategoryRecord]:
    """
    Returns a list of all child categories (leaf nodes).
    """

    categories = Category.objects.secondary().select_related("parent")

    return [category_record(category=category) for category in categories]


@cached(key=_category_navigation_active_list_key, timeout=5 * 60)
def category_navigation_active_list_from_cache() -> list[CategoryDetailRecord]:
    """
    Returns a list of active navigation categories from cache.
    """

    return category_navigation_active_list()


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
    Get a list of active parents for a single category instance. The
    .get_cached_trees() manager utility will only return nodes based
    on the highest node level from the queryset it is passed. E.g. if
    a primary category is a part of the returned queryset, only associated
    primary categories will be passed, and child nodes, even though they
    technically are parents of passed category, will be dropped.
    """

    parents = (
        category.get_ancestors().select_related("parent").active().get_cached_trees()
    )

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
        children = category.get_children().select_related("parent").order_by("ordering")
    else:
        children = (
            category.get_children()
            .select_related("parent")
            .active()
            .order_by("ordering")
        )

    return [category_record(category=child) for child in children]


def category_tree_active_list_for_product(
    *, product: Product
) -> list[CategoryDetailRecord]:
    """
    Get a full representation of a nested category tree connected to
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
        active_categories = (
            product.categories.active().select_related("parent").order_by("-mptt_level")
        )

    return [category_detail_record(category=category) for category in active_categories]
