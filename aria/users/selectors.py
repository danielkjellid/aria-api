from typing import Any, Optional, TypeVar

from aria.users.filters import UserFilter
from aria.users.models import User
from aria.users.records import UserRecord
from aria.users.schemas.filters import UserListFilters

T = TypeVar("T", bound=User)


def permissions_get_for_user(*, user: T) -> list[str]:
    """
    Aggregate both group and individual permissions for user.
    """

    prefetched_user_perms = getattr(user, "user_perms", None)
    prefetched_group_perms = getattr(user, "group_perms", None)

    if prefetched_user_perms is not None:
        user_perms = prefetched_user_perms
    else:
        user_perms = list(
            user.user_permissions.all().values_list("codename", flat=True)
        )

    if prefetched_group_perms is not None:
        group_perms = prefetched_group_perms
    else:
        group_perms = list(
            user.groups.all().values_list("permissions__codename", flat=True)
        )

    permissions = [
        codename for codename in set(user_perms + group_perms) if codename is not None
    ]

    return permissions


def user_list(
    *, filters: Optional[UserListFilters] | dict[str, Any] = None
) -> list[UserRecord]:
    """
    Returns a list of UserRecords of users based on given filters.
    """

    filters = filters or {}

    qs = User.objects.all().annotate_permissions().order_by("id")
    filtered_qs = UserFilter(filters, qs).qs

    return [
        UserRecord.from_user(user=user, permissions=permissions_get_for_user(user=user))
        for user in filtered_qs
    ]


def user_detail(*, pk: int) -> UserRecord | None:
    """
    Get the detailed representation of a single product based on id.
    """

    user = User.objects.filter(id=pk).annotate_permissions().first()

    if not user:
        return None

    return UserRecord.from_user(
        user=user, permissions=permissions_get_for_user(user=user)
    )
