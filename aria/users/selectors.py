from typing import Any, Optional

from aria.users.filters import UserFilter
from aria.users.models import User
from aria.users.records import UserProfileRecord, UserRecord
from aria.users.schemas.filters import UserListFilters


def user_record(*, user: User) -> UserRecord:
    """
    Get the record representation for a single user instance.
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

    return UserRecord(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        profile=UserProfileRecord(
            full_name=user.full_name,
            avatar_color=user.avatar_color,
            initial=user.initial,
        ),
        birth_date=user.birth_date,
        phone_number=user.phone_number,
        has_confirmed_email=user.has_confirmed_email,
        street_address=user.street_address,
        zip_code=user.zip_code,
        zip_place=user.zip_place,
        disabled_emails=user.disabled_emails,
        subscribed_to_newsletter=user.subscribed_to_newsletter,
        allow_personalization=user.allow_personalization,
        allow_third_party_personalization=user.allow_third_party_personalization,
        acquisition_source=user.acquisition_source,
        date_joined=user.date_joined,
        is_active=user.is_active,
        is_staff=user.is_staff,
        is_superuser=user.is_superuser,
        permissions=permissions if permissions else [],
    )


def user_list(
    *, filters: Optional[UserListFilters] | dict[str, Any] = None
) -> list[UserRecord]:
    """
    Returns a list of UserRecords of users based on given filters.
    """

    filters = filters or {}

    qs = User.objects.all().annotate_permissions().order_by("id")
    filtered_qs = UserFilter(filters, qs).qs

    return [user_record(user=user) for user in filtered_qs]


def user_detail(*, pk: int) -> UserRecord | None:
    """
    Get the detailed representation of a single product based on id.
    """

    user = User.objects.filter(id=pk).annotate_permissions().first()

    if not user:
        return None

    return user_record(user=user)
