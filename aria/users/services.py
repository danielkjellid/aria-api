from typing import Any, Optional
from django.utils import timezone
from django.db import transaction
from django.http import HttpRequest
from aria.core.services import model_update
from aria.users.models import User
from django.contrib.auth.models import Group
from django.utils.http import (
    urlsafe_base64_decode as uid_decoder,
)
from django.utils.encoding import force_text
from django.utils.translation import gettext as _

from aria.core.exceptions import ApplicationError

# TODO:
# - Add method for creating users
# - Upon creation, send confimation email


def user_create(
    *,
    email: str,
    password: Optional[str] = None,
    subscribed_to_newsletter: bool = True,
    send_verification_email: bool = False,
    group: Optional[Group] = None,
    request: Optional[HttpRequest] = None,
    is_staff: bool = False,
    is_active: bool = True,
    **additional_fields: Any,
) -> User:
    """
    Creates a new user instance.
    """

    if not email:
        raise ValueError("Email cannot be none.")

    existing_user = User.objects.get(email__iexact=email)

    if existing_user:
        raise ApplicationError(message=_("User with email already exists."))

    # Create the new user
    new_user = User(
        email=email,
        is_staff=is_staff,
        is_active=is_active,
        subscribed_to_newsletter=subscribed_to_newsletter,
        date_joined=timezone.now(),
        **additional_fields,
    )

    new_user.set_password(password)
    new_user.save()

    if group:
        new_user.groups.add(group)

    # TODO: add user channel

    if send_verification_email:
        # TODO: add send verification email method
        pass

    return new_user


@transaction.atomic
def user_update(*, user: User, data, log_change=True) -> User:
    """
    Updates an existing user instance.
    """

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
    ]

    user, has_updated, updated_fields = model_update(
        instance=user, fields=non_side_effect_fields, data=data
    )

    # TODO: implement logging

    return user


def user_verify_account(*, uid: str, token: str) -> None:

    try:
        decode_uid = force_text(uid_decoder(uid))
        user = User.objects.get(id=decode_uid)
    except User.DoesNotExist:
        raise ApplicationError(message=_("Unable to find user with provided uid."))

    if user.has_confirmed_email:
        raise ApplicationError(message=_("Account is already verified."))

    is_token_valid = user.validate_verification_email_token(token=token)

    if is_token_valid:
        user.has_confirmed_email = True
        user.save()
    else:
        raise ApplicationError(message=_("Token is invalid, please try again by."))
