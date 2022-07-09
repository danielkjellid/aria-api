from typing import Any, Optional

from django.conf import settings
from django.contrib.auth import password_validation
from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import validate_email
from django.db import transaction
from django.http import HttpRequest
from django.utils import timezone
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode as uid_decoder

from aria.audit_logs.services import log_entries_create
from aria.audit_logs.types import ChangeMessage
from aria.core.exceptions import ApplicationError
from aria.core.services import model_update
from aria.users.models import User
from aria.users.records import UserRecord
from aria.users.selectors import user_record


def _validate_email_and_password(email: str, password: str | None) -> tuple[str, str]:
    """
    Validate email and password for create operation
    """

    if not email:
        raise ValueError("Error when creating user, email cannot be none.")

    if not password:
        raise ValueError("Unable to validate email and password, password is none.")

    existing_user = User.objects.filter(email__iexact=email).exists()

    if existing_user:
        raise ApplicationError(message="User with email already exists.")

    try:
        validate_email(email)
    except DjangoValidationError as exc:
        raise ApplicationError(message=str(exc)) from exc

    try:
        validate_password(password)
    except DjangoValidationError as exc:
        raise ApplicationError(message=str(exc)) from exc

    return email, password


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
    site: Optional[Site] = None,
    **additional_fields: Any,
) -> UserRecord:
    """
    Creates a new user instance.
    """

    email, password = _validate_email_and_password(email=email, password=password)

    if not site:
        site = Site.objects.get(id=settings.SITE_ID)

    # Create the new user
    new_user = User(
        email=email,
        is_staff=is_staff,
        is_active=is_active,
        subscribed_to_newsletter=subscribed_to_newsletter,
        date_joined=timezone.now(),
        site=site,
        **additional_fields,
    )

    new_user.set_password(password)
    new_user.save()

    if group:
        new_user.groups.add(group)

    # TODO: add user channel

    if send_verification_email:
        new_user.send_verification_email()

    return user_record(user=new_user)


@transaction.atomic
def user_update(
    *, user: User, data: Any, author: Optional[User] = None, log_change: bool = True
) -> UserRecord:
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

    updated_user: User
    has_updated: bool
    updated_fields: list[ChangeMessage]

    updated_user, has_updated, updated_fields = model_update(
        instance=user, fields=non_side_effect_fields, data=data
    )

    if has_updated and author is not None and log_change:
        log_entries_create(
            author=author, instance=updated_user, change_messages=updated_fields
        )

    return user_record(user=updated_user)


def user_verify_account(*, uid: str, token: str) -> UserRecord:
    """
    Verify a user account, setting has_confirmed_email to True
    if given uid and token match.
    """

    try:
        decode_uid = force_str(uid_decoder(uid))
        user = User.objects.get(id=decode_uid)
    except User.DoesNotExist as exc:
        raise ApplicationError(
            message="Unable to find user with provided uid."
        ) from exc

    if user.has_confirmed_email:
        raise ApplicationError(message="Account is already verified.")

    is_token_valid = user.validate_verification_email_token(token=token)

    if not is_token_valid:
        raise ApplicationError(message="Token is invalid, please try again.")

    user.has_confirmed_email = True
    user.save()

    return user_record(user=user)


def user_set_password(*, uid: str, token: str, new_password: str) -> UserRecord:
    """
    Set new password for user, validating uid, token and password. Eventually
    sets a new password for the user.
    """

    try:
        decode_uid = force_str(uid_decoder(uid))
        user = User.objects.get(id=decode_uid)
    except User.DoesNotExist as exc:
        raise ApplicationError(
            message="Unable to find user with provided uid."
        ) from exc

    is_token_valid = default_token_generator.check_token(user, token)

    if not is_token_valid:
        raise ApplicationError(message="Token is invalid, please try again.")

    # Validate password, will raise ValidationError if password does not
    # meet requirements
    password_validation.validate_password(new_password, user)

    user.set_password(new_password)
    user.save()

    return user_record(user=user)
