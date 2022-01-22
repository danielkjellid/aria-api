from typing import List
from django.forms import DateTimeField
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.decorators.debug import sensitive_post_parameters
from rest_framework import filters, generics, status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import serializers

from django.http import HttpRequest, HttpResponse

from aria.audit_logs.models import LogEntry
from aria.audit_logs.selectors import logs_get
from aria.core.pagination import (
    LimitOffsetPagination,
    get_paginated_response,
)
from aria.core.permissions import HasUserOrGroupPermission
from aria.core.serializers import inline_serializer
from aria.notes.models import NoteEntry
from aria.notes.serializers import CreateNoteSerializer, UpdateNoteSerializer
from aria.users.models import User
from aria.users.selectors import user_get, user_list
from aria.users.serializers import (
    AccountVerificationConfirmSerializer,
    AccountVerificationSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetSerializer,
    RequestUserSerializer,
    UserCreateSerializer,
    UserNoteSerializer,
)
from aria.users.services import user_update

sensitive_post_parameters_m = method_decorator(
    sensitive_post_parameters(
        "password", "old_password", "new_password1", "new_password2"
    )
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
        default_limit = 18

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

    def get(self, request: HttpRequest) -> list["User"]:
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


class UserNoteAPIView(APIView):

    queryset = NoteEntry.objects.all()
    permission_classes = (IsAdminUser, HasUserOrGroupPermission)
    required_permissions = {
        "GET": ["has_users_list"],
        "POST": ["has_notes_add"],
        "PUT": ["has_note_edit"],
    }

    def get_object(self, pk):
        user = get_object_or_404(User, pk=pk)
        return user

    def get(self, request, pk):
        user = self.get_object(pk)
        user_notes = NoteEntry.get_notes(user)
        serializer = UserNoteSerializer(user_notes, many=True)
        return Response(serializer.data)

    def post(self, request, pk):
        user = self.get_object(pk)
        serializer = CreateNoteSerializer(data=request.data)

        if serializer.is_valid():
            NoteEntry.create_note(request.user, user, serializer.data["note"])
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):

        serializer = UpdateNoteSerializer(data=request.data)

        if serializer.is_valid():
            NoteEntry.update_note(
                request.user, serializer.data["id"], serializer.data["note"]
            )
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RequestUserRetrieveAPIView(generics.RetrieveAPIView):
    """
    View for getting info about request user
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = RequestUserSerializer

    def get(self, request):
        user = get_object_or_404(User, pk=request.user.id)
        serializer = self.serializer_class(user)

        return Response(serializer.data, status=status.HTTP_200_OK)


class UserCreateAPIView(generics.CreateAPIView):
    """
    View for creating a user instance
    """

    # set view public
    permission_classes = (AllowAny,)
    authentication_classes = ()

    # use the UserCreate serializer
    serializer_class = UserCreateSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetView(generics.GenericAPIView):
    """
    View for reseting password.

    Calls Django Auth PasswordResetForm save method.

    Accepts the following POST parameters: email
    Returns the success/fail message.
    """

    serializer_class = PasswordResetSerializer
    permission_classes = (AllowAny,)
    authentication_classes = ()

    def post(self, request, *args, **kwargs):
        """
        Create a serializer with request.data
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save()

        return Response(
            {"detail": _("Password reset e-mail has been sent.")},
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirmView(generics.GenericAPIView):
    """
    Password reset e-mail link is confirmed, therefore
    this resets the user's password.

    Accept the following POST parameters: token, uid, new_password1,
    new_password2

    Returns the success/fail message.
    """

    serializer_class = PasswordResetConfirmSerializer
    permission_classes = (AllowAny,)
    authentication_classes = ()

    @sensitive_post_parameters_m
    def dispatch(self, *args, **kwargs):
        return super(PasswordResetConfirmView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"detail": _("Password has been reset with the new password")},
            status=status.HTTP_200_OK,
        )


class AccountVerificationView(generics.GenericAPIView):
    """
    View for sending verification email.

    Accepts the following POST parameters: email
    Returns the success/fail message.
    """

    serializer_class = AccountVerificationSerializer
    permission_classes = (AllowAny,)
    authentication_classes = ()

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save()

        return Response(
            {"detail": _("Email verification has been sent.")},
            status=status.HTTP_200_OK,
        )


class AccountVerificationConfirmView(generics.GenericAPIView):
    """
    Verification e-mail link is confirmed, therefore
    this sets the user.has_confirmed_email to true.

    Accept the following POST parameters: token, uid

    Returns the success/fail message.
    """

    serializer_class = AccountVerificationConfirmSerializer
    permission_classes = (AllowAny,)
    authentication_classes = ()

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"detail": _("Account email verified")}, status=status.HTTP_200_OK
        )
