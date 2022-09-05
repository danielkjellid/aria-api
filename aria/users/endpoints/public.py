from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from ninja import Router

from aria.api.decorators import api
from aria.api.responses import codes_40x
from aria.api.schemas.responses import ExceptionResponse
from aria.api_auth.authentication import JWTAuthRequired
from aria.users.models import User
from aria.users.schemas.inputs import (
    UserAccountVerificationConfirmInput,
    UserAccountVerificationInput,
    UserCreateInput,
    UserPasswordResetConfirmInput,
    UserPasswordResetInput,
)
from aria.users.schemas.outputs import UserRequestOutput
from aria.users.selectors import user_detail
from aria.users.services import user_create, user_set_password, user_verify_account

router = Router(tags=["Users"])


@api(
    router,
    "me/",
    method="GET",
    response={200: UserRequestOutput},
    summary="Retrieve details about the user making the request",
    auth=JWTAuthRequired(),
)
def user_request_api(request: HttpRequest) -> tuple[int, UserRequestOutput]:
    """
    Retrieve details about the user making the request.
    """

    request_user = request.auth  # type:ignore
    user = user_detail(pk=request_user.id)

    if user is None:
        raise ObjectDoesNotExist(_("User does not exist."))

    return 200, UserRequestOutput(**user.dict())


@api(
    router,
    "create/",
    method="POST",
    response={201: None},
    summary="Creates a user",
)
def user_create_api(request: HttpRequest, payload: UserCreateInput) -> int:
    """
    Creates a single user instance.
    """

    user_create(**payload.dict(), send_verification_email=True)
    return 201


@api(
    router,
    "verify/",
    method="POST",
    response={200: None, codes_40x: ExceptionResponse},
    summary="Sends verification email",
)
def user_account_verification_api(
    request: HttpRequest, payload: UserAccountVerificationInput
) -> int:
    """
    Sends verification email to a specific email (user) for them to verify the account.
    """

    try:
        user = User.objects.get(email__iexact=payload.email, is_active=True)
    except User.DoesNotExist as exc:
        raise ObjectDoesNotExist(_("User does not exist.")) from exc

    user.send_verification_email()

    return 200


@api(
    router,
    "verify/confirm/",
    method="POST",
    response={200: None},
    summary="Validate email tokens to confirm account",
)
def user_account_verification_confirm_api(
    request: HttpRequest, payload: UserAccountVerificationConfirmInput
) -> int:
    """
    Takes uid and token present in verification email, validates them,
    and updates email to confirmed.
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
def user_password_reset_api(
    request: HttpRequest, payload: UserPasswordResetInput
) -> int:
    """
    Sends a password reset email to provided email, if user exist.
    """

    try:
        user = User.objects.get(email__iexact=payload.email, is_active=True)
    except User.DoesNotExist as exc:
        raise ObjectDoesNotExist from exc

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
    request: HttpRequest, payload: UserPasswordResetConfirmInput
) -> int:
    """
    Sets a password if provided uid and token is valid.
    """
    print("yoo?")
    user_set_password(
        uid=payload.uid,
        token=payload.token,
        new_password=payload.new_password,
        new_password2=payload.new_password2,
    )

    return 200
