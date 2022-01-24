from django.http import HttpRequest, HttpResponse
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from aria.core.pagination import LimitOffsetPagination, get_paginated_response
from aria.core.permissions import HasUserOrGroupPermission
from aria.core.serializers import inline_serializer
from aria.users.models import User
from aria.users.selectors import user_list
from aria.users.services import (
    user_update,
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
        is_active = serializers.BooleanField(allow_null=True)
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
                "author": serializers.CharField(),
                "change": serializers.JSONField(),
                "date_of_change": serializers.DateTimeField(),
            },
        )

    def get(self, request: HttpRequest, user_id: int) -> HttpResponse:
        user = get_object_or_404(User, pk=user_id)
        serializer = self.OutputSerializer(user)

        return Response(serializer.data, status=status.HTTP_200_OK)


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
        has_confirmed_email = serializers.BooleanField(allow_null=True, required=False)
        street_address = serializers.CharField(required=False)
        zip_code = serializers.CharField(required=False)
        zip_place = serializers.CharField(required=False)
        disabled_emails = serializers.BooleanField(allow_null=True, required=False)
        subscribed_to_newsletter = serializers.BooleanField(
            allow_null=True, required=False
        )
        allow_personalization = serializers.BooleanField(
            allow_null=True, required=False
        )
        allow_third_party_personalization = serializers.BooleanField(
            allow_null=True, required=False
        )

    def post(self, request: HttpRequest, user_id: int) -> HttpResponse:
        user = get_object_or_404(User, pk=user_id)
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_update(
            user=user,
            data=serializer.validated_data,
            author=request.user,
            log_change=True,
        )

        return Response(
            {
                "message": _("User was updated successfully"),
                "data": serializer.initial_data,
            },
            status=status.HTTP_200_OK,
        )
