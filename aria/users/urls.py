from django.urls import path, re_path

from aria.users.viewsets import (
    AccountVerificationConfirmView,
    AccountVerificationView,
    PasswordResetConfirmView,
    PasswordResetView,
    RequestUserRetrieveAPIView,
    UserCreateAPIView,
    UserDetailAPIView,
    UserNoteAPIView,
    UsersListAPIView,
)

urlpatterns = [
    # endpoint for getting all users
    path("", UsersListAPIView.as_view(), name="users_list"),
    # endpoint for getting info about request user
    path("user/", RequestUserRetrieveAPIView.as_view(), name="request_user"),
    # endpoint for getting a single user instance
    path("<int:pk>/", UserDetailAPIView.as_view(), name="user_detail"),
    path("<int:pk>/notes/", UserNoteAPIView.as_view(), name="user_notes"),
    # endpoint for creating a single user instance
    path("create/", UserCreateAPIView.as_view(), name="user_create"),
    path("password/reset/", PasswordResetView.as_view(), name="reset_password"),
    re_path(
        r"^password/reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$",
        PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path("verify/", AccountVerificationView.as_view(), name="verify_account"),
    re_path(
        r"^users/verify/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$",
        AccountVerificationConfirmView.as_view(),
        name="account_verification_confirm",
    ),
]
