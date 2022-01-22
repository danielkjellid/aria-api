from django.db import transaction
from aria.core.services import model_update
from aria.users.models import User

# TODO:
# - Add method for creating users
# - Upon creation, send confimation email


@transaction.atomic
def user_update(*, user: User, data, log_change=True) -> User:
    # Non side effect fields are field that does not have
    # any dependencies. E.g. fields that are not used in
    # the generation of for example other fields.
    non_side_effect_fields = [
        "email",
        "first_name",
        "last_name",
        "birth_date",
        "avatar_color",
        "phone_number",
        "has_confirmed_email",
        "street_address",
        "zip_code",
        "disabled_emails",
        "subscribed_to_newsletter",
        "allow_personalization",
        "allow_third_party_personalization",
        "acquisition_source",
        "date_joined",
        "is_active",
        "is_staff",
        "is_superuser",
    ]

    user, has_updated, updated_fields = model_update(
        instance=user, fields=non_side_effect_fields, data=data
    )

    # TODO: implement logging

    return user
