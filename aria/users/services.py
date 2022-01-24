from typing import Any, Optional

from django.contrib.auth import password_validation
from django.contrib.auth.models import Group
from django.contrib.auth.tokens import default_token_generator
from django.db import transaction
from django.http import HttpRequest
from django.utils import timezone
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode as uid_decoder
from django.utils.translation import gettext as _
from aria.audit_logs.services import log_entry_create

from aria.core.exceptions import ApplicationError
from aria.core.services import model_update
from aria.users.models import User


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
        raise ValueError("Error when creating user, email cannot be none.")

    existing_user = User.objects.filter(email__iexact=email).exists()

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
        new_user.send_verification_email()

    return new_user


@transaction.atomic
def user_update(
    *, user: User, data, author: Optional[User] = None, log_change=True
) -> User:
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
        "zip_place",
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

    if has_updated and author is not None and log_change:
        log_entry_create(author=author, instance=user, change_messages=updated_fields)

    return user


def user_verify_account(*, uid: str, token: str) -> None:
    """
    Verify a user account, setting has_confirmed_email to True
    if given uid and token match.
    """

    try:
        decode_uid = force_str(uid_decoder(uid))
        user = User.objects.get(id=decode_uid)
    except User.DoesNotExist:
        raise ApplicationError(message=_("Unable to find user with provided uid."))

    if user.has_confirmed_email:
        raise ApplicationError(message=_("Account is already verified."))

    is_token_valid = user.validate_verification_email_token(token=token)

    if not is_token_valid:
        raise ApplicationError(message=_("Token is invalid, please try again."))

    print("user", user.id)

    user.has_confirmed_email = True
    user.save()


def user_set_password(*, uid: str, token: str, new_password: str) -> None:
    """
    Set new password for user, validating uid, token and password. Eventually
    sets a new password for the user.
    """

    try:
        decode_uid = force_str(uid_decoder(uid))
        user = User.objects.get(id=decode_uid)
    except User.DoesNotExist:
        raise ApplicationError(message=_("Unable to find user with provided uid."))

    is_token_valid = default_token_generator.check_token(user, token)

    if not is_token_valid:
        raise ApplicationError(message=_("Token is invalid, please try again."))

    # Validate password, will raise ValidationError if password does not
    # meet requirements
    password_validation.validate_password(new_password, user)

    user.set_password(new_password)
    user.save()
