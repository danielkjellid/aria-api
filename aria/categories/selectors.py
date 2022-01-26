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
