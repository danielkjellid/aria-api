from typing import List, Union

from django.contrib.auth.models import Permission
from django.db.models import QuerySet

from aria.users.filters import UserFilter
from aria.users.models import User


def get_user_permissions(user: User) -> List[str]:
    """
    Returns a list of a specific users permission names.
    """

    if not user.is_authenticated:
        return None

    permissions = Permission.objects.filter(user=user).values_list(
        "codename", flat=True
    )

    return permissions


def get_user_group_permissions(user: User) -> List[str]:
    """
    Return a list of a users' group permission names.
    """

    if not user.is_authenticated:
        return None

    group_permissions = Permission.objects.filter(group__user=user).values_list(
        "codename", flat=True
    )

    return group_permissions


def user_list(*, filters=None) -> Union[QuerySet, List[User]]:
    """
    Returns a queryset of users based on given filters.
    """

    filters = filters or {}

    qs = User.objects.all()

    return UserFilter(filters, qs).qs
