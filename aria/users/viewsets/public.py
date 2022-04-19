from django.http import HttpRequest, HttpResponse
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from aria.core.exceptions import ApplicationError
from aria.core.schemas import APIViewSchema
from aria.users.models import User
from aria.users.services import user_create, user_set_password, user_verify_account


class UserCreateAPI(APIView):
    """
    [PUBLIC] Endpoint for creating a new user instance.

    Returns the created user.
    """

    permission_classes = (AllowAny,)
    authentication_classes = ()
    schema = APIViewSchema()

    class InputSerializer(serializers.Serializer):
        email = serializers.EmailField()
        first_name = serializers.CharField()
        last_name = serializers.CharField()
        phone_number = serializers.CharField()
        street_address = serializers.CharField()
        zip_code = serializers.CharField()
        zip_place = serializers.CharField()
        subscribed_to_newsletter = serializers.BooleanField(allow_null=True)
        allow_personalization = serializers.BooleanField(allow_null=True)
        allow_third_party_personalization = serializers.BooleanField(allow_null=True)
        password = serializers.CharField(min_length=8, write_only=True)

    @APIViewSchema.serializer(InputSerializer())
    def post(self, request: HttpRequest) -> HttpResponse:
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = user_create(**serializer.validated_data)

        return Response(
            {
                "message": _("Account has been created."),
                "data": self.InputSerializer(user).data,
            },
            status=status.HTTP_201_CREATED,
        )


class UserAccountVerificationAPI(APIView):
    """
    [PUBLIC] Endpoint for sending a verification email to the user.
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
            user = User.objects.get(email__iexact=serializer.validated_data["email"])
        except User.DoesNotExist:
            raise ApplicationError(_("User does not exist."))

        user.send_verification_email()

        return Response(
            {"message": _("Email verification has been sent."), "data": {}},
            status=status.HTTP_200_OK,
        )


class UserAccountVerificationConfirmAPI(APIView):
    """
    [PUBLIC] Endpoint for validating email tokens.
    """

    permission_classes = (AllowAny,)
    authentication_classes = ()
    schema = APIViewSchema()

    class InputSerializer(serializers.Serializer):
        uid = serializers.CharField()
        token = serializers.CharField()

    @APIViewSchema.serializer(InputSerializer())
    def post(self, request: HttpRequest, uid: str, token: str) -> HttpResponse:
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_verify_account(uid=uid, token=token)

        return Response(
            {"message": _("Account email verified."), "data": {}},
            status=status.HTTP_200_OK,
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
            raise ApplicationError(message=_("User does not exist."))

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
