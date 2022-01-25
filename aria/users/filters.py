from django_filters import FilterSet

from aria.users.models import User


class UserFilter(FilterSet):
    """
    A set of searchable fields for the user model.
    """

    class Meta:
        model = User
        fields = ("email", "first_name", "last_name", "phone_number")
