from typing import Union

from django.db.models import QuerySet

from aria.users.filters import UserFilter
from aria.users.models import User


def user_list(*, filters=None) -> Union[QuerySet, User]:
    """
    Returns a queryset of users based on given filters.
    """

    filters = filters or {}

    qs = User.objects.all()

    return UserFilter(filters, qs).qs
