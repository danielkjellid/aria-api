from typing import List, Union
from django.contrib.auth.models import Permission
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from aria.notes.models import NoteEntry
from aria.notes.selectors import notes_for_instance_get

from aria.users.models import User
from aria.users.filters import UserFilter


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
    filters = filters or {}

    qs = User.objects.all()

    return UserFilter(filters, qs).qs


def user_get(*, id=None) -> User:
    return get_object_or_404(User, id)


def user_notes_list(*, user: User) -> Union[QuerySet, NoteEntry]:
    return notes_for_instance_get(instance=user)
