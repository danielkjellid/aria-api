from django.urls import path, re_path

from aria.users.viewsets import (
    AccountVerificationConfirmView,
    PasswordResetConfirmView,
    PasswordResetView,
    RequestUserRetrieveAPIView,
    UserUpdateAPI,
    UserListAPI,
    UserDetailAPI,
    UserCreateAPI,
    UserNoteListAPI,
    UserAuditLogsListAPI,
    UserAccountVerificationAPI,
)

urlpatterns = [
    # Endpoint for getting all users
    path("", UserListAPI.as_view(), name="user-list"),
    path("create/", UserCreateAPI.as_view(), name="user-create"),
    path("verify/", UserAccountVerificationAPI.as_view(), name="user-verify"),
    path("<int:user_id>/", UserDetailAPI.as_view(), name="user-detail"),
    path("<int:user_id>/update/", UserUpdateAPI.as_view(), name="user-update"),
    path("<int:user_id>/notes/", UserNoteListAPI.as_view(), name="user-notes"),
    path("<int:user_id>/logs/", UserAuditLogsListAPI.as_view(), name="user-logs"),
    # -------------------
    # Not yet refactored
    # ------------------
    # endpoint for getting info about request user
    path("user/", RequestUserRetrieveAPIView.as_view(), name="request_user"),
    # endpoint for getting a single user instance
    # endpoint for creating a single user instance
    path("users/password/reset/", PasswordResetView.as_view(), name="reset_password"),
    re_path(
        r"^users/password/reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$",
        PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    re_path(
        r"^users/verify/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$",
        AccountVerificationConfirmView.as_view(),
        name="account_verification_confirm",
    ),
]
