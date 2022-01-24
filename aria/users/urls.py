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
    path("", UserListAPI.as_view(), name="user-list"),
    path("<int:user_id>/", UserDetailAPI.as_view(), name="user-detail"),
    path("<int:user_id>/update/", UserUpdateAPI.as_view(), name="user-update"),
]

public_patterns = [
    path("create/", UserCreateAPI.as_view(), name="user-create"),
    path("verify/", UserAccountVerificationAPI.as_view(), name="user-verify"),
    path(
        "verify/confirm/<str:uid>/<str:token>/",
        UserAccountVerificationConfirmAPI.as_view(),
        name="user-verify-confirm",
    ),
    path("password/reset/", UserPasswordResetAPI.as_view(), name="user-reset-password"),
    path(
        "password/reset/confirm/<str:uid>/<str:token>/",
        UserPasswordResetConfirmAPI.as_view(),
        name="user-reset-password-confirm",
    ),
]

urlpatterns = internal_patterns + public_patterns
