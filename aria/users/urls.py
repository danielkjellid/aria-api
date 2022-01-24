from django.urls import path

from aria.users.viewsets.internal import (
    UserDetailAPI,
    UserListAPI,
    UserUpdateAPI,
)

from aria.users.viewsets.public import (
    UserAccountVerificationAPI,
    UserAccountVerificationConfirmAPI,
    UserCreateAPI,
    UserPasswordResetAPI,
    UserPasswordResetConfirmAPI,
)

internal_patterns = [
    path("", UserListAPI.as_view(), name="users-list"),
    path("<int:user_id>/", UserDetailAPI.as_view(), name="users-detail"),
    path("<int:user_id>/update/", UserUpdateAPI.as_view(), name="users-update"),
]

public_patterns = [
    path("create/", UserCreateAPI.as_view(), name="users-create"),
    path("verify/", UserAccountVerificationAPI.as_view(), name="users-verify"),
    path(
        "verify/confirm/<str:uid>/<str:token>/",
        UserAccountVerificationConfirmAPI.as_view(),
        name="users-verify-confirm",
    ),
    path(
        "password/reset/", UserPasswordResetAPI.as_view(), name="users-reset-password"
    ),
    path(
        "password/reset/confirm/<str:uid>/<str:token>/",
        UserPasswordResetConfirmAPI.as_view(),
        name="users-reset-password-confirm",
    ),
]

urlpatterns = internal_patterns + public_patterns
