from django.http import HttpRequest, HttpResponse
from django.utils.translation import gettext as _
from django.shortcuts import get_object_or_404
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from aria.core.exceptions import ApplicationError
from aria.core.schemas import APIViewSchema
from aria.api.decorators import api
from aria.api.responses import GenericResponse
from aria.users.models import User
from aria.users.schemas import (
    UserCreateInput,
    UserCreateOutput,
    UserAccountVerificationInput,
    UserAccountVerificationConfirmInput,
    UserPasswordResetInput,
)
from aria.users.services import user_create, user_set_password, user_verify_account

from ninja import Router, Schema

router = Router()


@api(
    router,
    "create/",
    method="POST",
    response={201: GenericResponse},
    summary="Creates a user",
    description="Creates a single user instance",
    url_name="users-create",
)
def user_create_api(request, payload: UserCreateInput) -> tuple[int, GenericResponse]:
    """
    [PUBLIC] Endpoint for creating a new user instance.

    Returns the created user.
    """

    user = user_create(**payload.dict())

    return 201, GenericResponse(
        message=_("Account has been created."), data=UserCreateOutput.from_orm(user)
    )


@api(
    router,
    "verify/",
    method="POST",
    response={200: GenericResponse},
    summary="Sends verification email",
    description="Sends verification email to a specific email (user) for them to verify the account",
    url_name="users-verify",
)
def user_account_verification_api(
    request, payload: UserAccountVerificationInput
) -> tuple[int, GenericResponse]:
    """
    [PUBLIC] Endpoint for sending a verification email to the user.
    """

    try:
        user = User.objects.get(email__iexact=payload.email, is_active=True)
    except User.DoesNotExist:
        raise ApplicationError(_("User does not exist."), status_code=404)

    user.send_verification_email()

    return 200, GenericResponse(message=_("Email verification has been sent."), data={})


@api(
    router,
    "verify/confirm/",
    method="POST",
    response={200: GenericResponse},
    summary="Validate email tokens to confirm account",
    description="Takes uid and token present in verification email, validates them, and updates email to confirmed.",
    url_name="users-verify-confirm",
)
def user_account_verification_confirm_api(
    request, payload: UserAccountVerificationConfirmInput
) -> tuple[int, GenericResponse]:
    """
    [PUBLIC] Endpoint for validating email tokens.
    """

    user_verify_account(uid=payload.uid, token=payload.token)
    return 200, GenericResponse(message=_("Account email verified."), data={})


@api(
    router,
    "password/reset/",
    method="POST",
    response={200: GenericResponse},
    summary="Send a reset password email",
    description="Sends a password reset email to provided email, if user exist.",
    url_name="users-password-reset",
)
def user_password_reset_api(request, payload: UserPasswordResetInput):
    try:
        user = User.objects.get(email__iexact=payload.email, is_active=True)
    except User.DoesNotExist:
        raise ApplicationError(message=_("User does not exist."), status_code=404)

    user.send_password_reset_email(request=request)

    return 200, GenericResponse(
        message=_("Password reset e-mail has been sent."), data={}
    )


class UserPasswordResetAPI(APIView):
    """
    [PUBLIC] Endpoint for sending a password reset
    email.
    """

    permission_classes = (AllowAny,)
    authentication_classes = ()
    schema = APIViewSchema()

    class InputSerializer(serializers.Serializer):
        email = serializers.EmailField()

    @APIViewSchema.serializer(InputSerializer())
    def post(self, request: HttpRequest) -> HttpResponse:
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user = User.objects.get(
                email__iexact=serializer.validated_data["email"], is_active=True
            )
        except User.DoesNotExist:
            raise ApplicationError(message=_("User does not exist."), status_code=404)

        user.send_password_reset_email(request=request)

        return Response(
            {"message": _("Password reset e-mail has been sent."), "data": {}},
            status=status.HTTP_200_OK,
        )


class UserPasswordResetConfirmAPI(APIView):
    """
    [PUBLIC] Endpoint for setting a new password.
    """

    permission_classes = (AllowAny,)
    authentication_classes = ()
    schema = APIViewSchema()

    class InputSerializer(serializers.Serializer):
        new_password = serializers.CharField(max_length=128)
        uid = serializers.CharField()
        token = serializers.CharField()

    @APIViewSchema.serializer(InputSerializer())
    def post(self, request: HttpRequest, uid: str, token: str) -> HttpResponse:
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_set_password(**serializer.validated_data)

        return Response(
            {"message": _("Password has been reset with the new password"), "data": {}},
            status=status.HTTP_200_OK,
        )
