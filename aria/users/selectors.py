from django.contrib.auth.models import Permission

from aria.users.models import User


def get_user_permissions(user: User) -> list:
    """
    Returns a list of a specific users permission names.
    """

    if not user.is_authenticated:
        return None

    permissions = Permission.objects.filter(user=user).values_list(
        "codename", flat=True
    )

    return permissions


def get_user_group_permissions(user: User) -> list:
    """
    Return a list of a users' group permission names.
    """

    if not user.is_authenticated:
        return None

    group_permissions = Permission.objects.filter(group__user=user).values_list(
        "codename", flat=True
    )

    return group_permissions
