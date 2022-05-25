from django.utils.translation import gettext as _

from ninja import Router

from aria.api.decorators import api
from aria.api.responses import codes_40x
from aria.api.schemas.responses import ExceptionResponse
from aria.core.exceptions import ApplicationError
from aria.users.models import User
from aria.users.schemas.inputs import (
    UserAccountVerificationConfirmInput,
    UserAccountVerificationInput,
    UserCreateInput,
    UserPasswordResetConfirmInput,
    UserPasswordResetInput,
)
from aria.users.services import user_create, user_set_password, user_verify_account

router = Router(tags=["Users"])


@api(
    router,
    "create/",
    method="POST",
    response={201: None},
    summary="Creates a user",
)
def user_create_api(request, payload: UserCreateInput) -> int:
    """
    Creates a single user instance.
    """

    user_create(**payload.dict())
    return 201


@api(
    router,
    "verify/",
    method="POST",
    response={200: None, codes_40x: ExceptionResponse},
    summary="Sends verification email",
)
def user_account_verification_api(
    request, payload: UserAccountVerificationInput
) -> int:
    """
    Sends verification email to a specific email (user) for them to verify the account.
    """

    try:
        user = User.objects.get(email__iexact=payload.email, is_active=True)
    except User.DoesNotExist:
        raise ApplicationError(_("User does not exist."), status_code=404)

    user.send_verification_email()

    return 200


@api(
    router,
    "verify/confirm/",
    method="POST",
    response={200: None, codes_40x: ExceptionResponse},
    summary="Validate email tokens to confirm account",
)
def user_account_verification_confirm_api(
    request, payload: UserAccountVerificationConfirmInput
) -> int:
    """
    Takes uid and token present in verification email, validates them, and updates email to confirmed.
    """

    user_verify_account(uid=payload.uid, token=payload.token)
    return 200


@api(
    router,
    "password/reset/",
    method="POST",
    response={200: None, codes_40x: ExceptionResponse},
    summary="Send a reset password email",
)
def user_password_reset_api(request, payload: UserPasswordResetInput) -> int:
    """
    Sends a password reset email to provided email, if user exist.
    """

    try:
        user = User.objects.get(email__iexact=payload.email, is_active=True)
    except User.DoesNotExist:
        raise ApplicationError(message=_("User does not exist."), status_code=404)

    user.send_password_reset_email(request=request)

    return 200


@api(
    router,
    "password/reset/confirm/",
    method="POST",
    response={200: None, codes_40x: ExceptionResponse},
    summary="Send a reset password email",
)
def user_password_reset_confirm_api(
    request, payload: UserPasswordResetConfirmInput
) -> int:
    """
    Sets a password if provided uid and token is valid.
    """

    user_set_password(
        uid=payload.uid, token=payload.token, new_password=payload.new_password
    )

    return 200
