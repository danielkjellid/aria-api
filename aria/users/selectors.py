from typing import Any, Optional

from aria.core.records import SiteRecord
from aria.users.filters import UserFilter
from aria.users.models import User
from aria.users.records import UserProfileRecord, UserRecord
from aria.users.schemas.filters import UserListFilters


def user_record(*, user: User) -> UserRecord:
    """
    Get the record representation for a single user instance.
    """

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
        site=SiteRecord(name=user.site.name, domain=user.site.domain)
        if user.site
        else None,
    )


def user_list(
    *, filters: Optional[UserListFilters] | dict[str, Any] = None
) -> list[UserRecord]:
    """
    Returns a queryset of users based on given filters.
    """

    filters = filters or {}

    qs = User.objects.all().select_related("site")
    filtered_qs = UserFilter(filters, qs).qs.order_by("id")

    return [user_record(user=user) for user in filtered_qs]
