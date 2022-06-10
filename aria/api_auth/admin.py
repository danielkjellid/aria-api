from datetime import datetime
from typing import Any

from django.contrib import admin
from django.db.models import Model
from django.http import HttpRequest

from aria.api_auth.models import BlacklistedToken, OutstandingToken
from aria.core.models import BaseQuerySet
from aria.users.models import User


@admin.register(OutstandingToken)
class OutstandingTokenAdmin(admin.ModelAdmin):
    list_display = ("jti", "user", "created_at", "expires_at")
    search_fields = ("user__name", "user__email", "user__id", "jti")
    ordering = ("user",)
    actions = None

    def get_queryset(self, *args: Any, **kwargs: Any) -> BaseQuerySet[OutstandingToken]:
        qs: BaseQuerySet[OutstandingToken] = super().get_queryset(*args, **kwargs)

        return qs.select_related("user")

    def get_readonly_fields(self, *args: Any, **kwargs: Any) -> list[str]:
        return [f.name for f in self.model._meta.fields]

    def has_add_permission(self, *args: Any, **kwargs: Any) -> bool:
        return False

    def has_delete_permission(self, *args: Any, **kwargs: Any) -> bool:
        return False

    def has_change_permission(
        self, request: HttpRequest, obj: Model | None = None
    ) -> bool:
        if request.method in [
            "GET",
            "HEAD",
        ] and super().has_change_permission(request, obj):
            return True
        return False


@admin.register(BlacklistedToken)
class BlacklistedTokenAdmin(admin.ModelAdmin):
    list_display = (
        "token_jti",
        "token_user",
        "token_created_at",
        "token_expires_at",
        "blacklisted_at",
    )
    search_fields = (
        "token__user__name",
        "token__user__email",
        "token__user__id",
        "token__jti",
    )
    ordering = ("token__user",)

    def get_queryset(self, *args: Any, **kwargs: Any) -> BaseQuerySet[BlacklistedToken]:
        qs: BaseQuerySet[BlacklistedToken] = super().get_queryset(*args, **kwargs)

        return qs.select_related("token__user")

    @staticmethod
    def token_jti(obj: BlacklistedToken) -> BaseQuerySet[BlacklistedToken]:
        return obj.token.jti

    token_jti.short_description = "jti"
    token_jti.admin_order_field = "token__jti"

    @staticmethod
    def token_user(obj: BlacklistedToken) -> User:
        return obj.token.user

    token_user.short_description = "user"
    token_user.admin_order_field = "token__user"

    @staticmethod
    def token_created_at(obj: BlacklistedToken) -> datetime:
        return obj.token.created_at

    token_created_at.short_description = "created at"
    token_created_at.admin_order_field = "token__created_at"

    @staticmethod
    def token_expires_at(obj: BlacklistedToken) -> datetime:
        return obj.token.expires_at

    token_expires_at.short_description = "expires at"
    token_expires_at.admin_order_field = "token__expires_at"
