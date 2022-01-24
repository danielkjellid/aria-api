from django.http import HttpRequest, HttpResponse
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from aria.core.exceptions import ApplicationError
from aria.core.pagination import LimitOffsetPagination, get_paginated_response
from aria.core.permissions import HasUserOrGroupPermission
from aria.core.serializers import inline_serializer
from aria.users.models import User
from aria.users.selectors import user_list
from aria.users.services import (
    user_create,
    user_set_password,
    user_update,
    user_verify_account,
)


class UserListAPI(APIView):
    """
    Endpoint for listing all registered users.

    Returns a list of users.
    """

    permission_classes = (IsAdminUser, HasUserOrGroupPermission)
    required_permissions = {
        "GET": ["has_users_list"],
    }

    class Pagination(LimitOffsetPagination):
        limit = 18

    class FilterSerializer(serializers.Serializer):
        email = serializers.EmailField(required=False)
        first_name = serializers.CharField(required=False)
        last_name = serializers.CharField(required=False)
        phone_number = serializers.CharField(required=False)

    class OutputSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        email = serializers.EmailField()
        is_active = serializers.NullBooleanField()
        date_joined = serializers.DateTimeField()
        profile = inline_serializer(
            source="*",
            fields={
                "full_name": serializers.CharField(),
                "initial": serializers.CharField(),
                "avatar_color": serializers.CharField(),
            },
        )

    def get(self, request: HttpRequest) -> HttpResponse:
        # Make sure the filters are valid, if passed
        filters_serializer = self.FilterSerializer(data=request.query_params)
        filters_serializer.is_valid(raise_exception=True)

        # Get all users in the app
        users = user_list(filters=filters_serializer.validated_data).order_by("id")

        return get_paginated_response(
            pagination_class=self.Pagination,
            serializer_class=self.OutputSerializer,
            queryset=users,
            request=request,
            view=self,
        )


class UserDetailAPI(APIView):
    """
    Endpoint for listing a specific user. Takes the
    user id as a parameter.

    Returns a single user instance.
    """

    permission_classes = (IsAdminUser, HasUserOrGroupPermission)
    required_permissions = {
        "GET": ["has_users_list"],
    }

    class OutputSerializer(serializers.Serializer):
        # User data
        first_name = serializers.CharField()
        last_name = serializers.CharField()
        email = serializers.EmailField()
        phone_number = serializers.CharField(source="formatted_phone_number")
        birth_date = serializers.DateField()
        has_confirmed_email = serializers.BooleanField()

        # Account data
        last_login = serializers.DateTimeField()
        id = serializers.IntegerField()
        profile = inline_serializer(
            source="*",
            read_only=True,
            fields={
                "full_name": serializers.CharField(),
                "initial": serializers.CharField(),
                "avatar_color": serializers.CharField(),
            },
        )
        date_joined = serializers.DateTimeField()
        is_active = serializers.BooleanField()

        # Address data
        full_address = serializers.CharField()
        street_address = serializers.CharField()
        zip_code = serializers.CharField()
        zip_place = serializers.CharField()

        # Marketing data
        acquisition_source = serializers.CharField()
        disabled_emails = serializers.BooleanField()
        subscribed_to_newsletter = serializers.BooleanField()
        allow_personalization = serializers.BooleanField()
        allow_third_party_personalization = serializers.BooleanField()

        # Notes and logs
        notes = inline_serializer(
            source="get_notes",
            many=True,
            read_only=True,
            fields={
                "id": serializers.IntegerField(),
                "note": serializers.CharField(),
                "updated_at": serializers.DateTimeField(),
                "author": inline_serializer(
                    source="user",
                    fields={
                        "full_name": serializers.CharField(),
                        "initial": serializers.CharField(),
                        "avatar_color": serializers.CharField(),
                    },
                ),
            },
        )
        logs = inline_serializer(
            source="get_audit_logs",
            many=True,
            read_only=True,
            fields={
                "user": serializers.CharField(),
                "change": serializers.JSONField(),
                "date_of_change": serializers.DateTimeField(),
            },
        )

    def get(self, request: HttpRequest, user_id: int) -> HttpResponse:
        user = get_object_or_404(User, pk=user_id)
        serializer = self.OutputSerializer(user)

        return Response(serializer.data)


class UserUpdateAPI(APIView):
    """
    Endpoint for updating a specific user. Takes the
    user id as a parameter and field(s) as payload.

    Returns a updated field(s).
    """

    permission_classes = (IsAdminUser, HasUserOrGroupPermission)
    required_permissions = {
        "POST": ["has_user_edit"],
    }

    class InputSerializer(serializers.Serializer):
        email = serializers.EmailField(required=False)
        first_name = serializers.CharField(required=False)
        last_name = serializers.CharField(required=False)
        phone_number = serializers.CharField(required=False)
        has_confirmed_email = serializers.NullBooleanField(required=False)
        street_address = serializers.CharField(required=False)
        zip_code = serializers.CharField(required=False)
        zip_place = serializers.CharField(required=False)
        disabled_emails = serializers.NullBooleanField(required=False)
        subscribed_to_newsletter = serializers.NullBooleanField(required=False)
        allow_personalization = serializers.NullBooleanField(required=False)
        allow_third_party_personalization = serializers.NullBooleanField(required=False)

    def post(self, request: HttpRequest, user_id: int) -> HttpResponse:
        user = get_object_or_404(User, pk=user_id)
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_update(user=user, data=serializer.validated_data)

        return Response(serializer.data, status=status.HTTP_200_OK)


class UserCreateAPI(APIView):
    """
    [PUBLIC] Endpoint for creating a new user instance.

    Returns the created user.
    """

    permission_classes = (AllowAny,)
    authentication_classes = ()

    class InputSerializer(serializers.Serializer):
        email = serializers.EmailField()
        first_name = serializers.CharField()
        last_name = serializers.CharField()
        phone_number = serializers.CharField()
        has_confirmed_email = serializers.NullBooleanField()
        street_address = serializers.CharField()
        zip_code = serializers.CharField()
        zip_place = serializers.CharField()
        disabled_emails = serializers.NullBooleanField()
        subscribed_to_newsletter = serializers.NullBooleanField()
        allow_personalization = serializers.NullBooleanField()
        allow_third_party_personalization = serializers.NullBooleanField()
        password = serializers.CharField(min_length=8, write_only=True)

    def post(self, request: HttpRequest) -> HttpResponse:
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = user_create(**serializer.validated_data)

        return Response(self.InputSerializer(user).data, status=status.HTTP_201_CREATED)


class UserNoteListAPI(APIView):
    """
    Endpoint for getting notes related to a user instance.

    Returns a list of notes bellonging to that user.
    """

    permission_classes = (IsAdminUser, HasUserOrGroupPermission)
    required_permissions = {
        "GET": ["has_notes_list"],
    }

    class Pagination(LimitOffsetPagination):
        limit = 20

    class OutputSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        note = serializers.CharField()
        updated_at = serializers.DateTimeField()
        author = inline_serializer(
            source="user",
            fields={
                "full_name": serializers.CharField(),
                "initial": serializers.CharField(),
                "avatar_color": serializers.CharField(),
            },
        )

    def get(self, request: HttpRequest, user_id: int) -> HttpResponse:
        user = get_object_or_404(User, pk=user_id)
        notes_of_user = user.get_notes()

        data = self.OutputSerializer(notes_of_user, many=True).data

        return Response(data, status=status.HTTP_200_OK)


class UserAuditLogsListAPI(APIView):
    """
    Endpoint for getting audit logs related to a user instance.

    Returns a list of logs on changes to that user.
    """

    permission_classes = (IsAdminUser, HasUserOrGroupPermission)
    required_permissions = {
        "GET": ["has_audit_logs_list"],
    }

    class Pagination(LimitOffsetPagination):
        limit = 20

    class OutputSerializer(serializers.Serializer):
        user = serializers.CharField()
        change = serializers.JSONField()
        date_of_change = serializers.DateTimeField()

    def get(self, request: HttpRequest, user_id: int) -> HttpResponse:
        user = get_object_or_404(User, pk=user_id)
        logs_of_user = user.get_audit_logs()

        data = self.OutputSerializer(logs_of_user, many=True).data

        return Response(data, status=status.HTTP_200_OK)


class UserAccountVerificationAPI(APIView):
    """
    [PUBLIC] Endpoint for sending a verification email to the user.
    """

    permission_classes = (AllowAny,)
    authentication_classes = ()

    class InputSerializer(serializers.Serializer):
        email = serializers.EmailField()

    def post(self, request: HttpRequest) -> HttpResponse:
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user = User.objects.get(email__iexact=serializer.validated_data["email"])
        except User.DoesNotExist:
            raise ApplicationError(_("User does not exist."))

        user.send_verification_email()

        return Response(
            {"detail": _("Email verification has been sent.")},
            status=status.HTTP_200_OK,
        )


class UserAccountVerificationConfirmAPI(APIView):
    """
    [PUBLIC] Endpoint for validating email tokens.
    """

    permission_classes = (AllowAny,)
    authentication_classes = ()

    class InputSerializer(serializers.Serializer):
        uid = serializers.CharField()
        token = serializers.CharField()

    def post(self, request: HttpRequest, uid: str, token: str) -> HttpResponse:
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_verify_account(uid=uid, token=token)

        return Response(
            {"detail": _("Account email verified.")},
            status=status.HTTP_200_OK,
        )


class UserPasswordResetAPI(APIView):
    """
    [PUBLIC] Endpoint for sending a password reset
    email.
    """

    permission_classes = (AllowAny,)
    authentication_classes = ()

    class InputSerializer(serializers.Serializer):
        email = serializers.EmailField()

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
            {"detail": _("Password reset e-mail has been sent.")},
            status=status.HTTP_200_OK,
        )


class UserPasswordResetConfirmAPI(APIView):
    """
    [PUBLIC] Endpoint for setting a new password.
    """

    permission_classes = (AllowAny,)
    authentication_classes = ()

    class InputSerializer(serializers.Serializer):
        new_password = serializers.CharField(max_length=128)
        uid = serializers.CharField()
        token = serializers.CharField()

    def post(self, request: HttpRequest, uid: str, token: str) -> HttpResponse:
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_set_password(**serializer.validated_data)

        return Response(
            {"detail": _("Password has been reset with the new password")},
            status=status.HTTP_200_OK,
        )
