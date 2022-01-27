from typing import Union

from django.db.models import QuerySet

from aria.categories.models import Category


def categories_navigation_list() -> Union[QuerySet, Category]:
    """
    Returns a queryset of navigation categories.
    """

    return Category.objects.primary_and_secondary().get_cached_trees()


def categories_navigation_active_list() -> Union[QuerySet, Category]:
    """
    Returns a queryset of active navigation categories.
    """

    return Category.objects.primary_and_secondary().active().get_cached_trees()


def categories_parent_active_list() -> Union[QuerySet, Category]:
    """
    Returns a queryset of active first level categories (is_primary)
    """

    return Category.objects.primary().active().get_cached_trees()


def categories_children_active_list(parent: Category) -> Union[QuerySet, Category]:
    """
    Returns a queryset of active second level categories (is_secondary)
    """

    # Check if cached children exist. If not cached, filter
    # children to get active, as it gets all children by default.
    if hasattr(parent, "_cached_children"):
        children = parent.get_children()
    else:
        children = parent.get_children().active()

    return children
