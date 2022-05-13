from django.urls import path

from aria.users.viewsets.internal import UserDetailAPI, UserListAPI, UserUpdateAPI

internal_patterns = [
    path("", UserListAPI.as_view(), name="users-list"),
    path("<int:user_id>/", UserDetailAPI.as_view(), name="users-detail"),
    path("<int:user_id>/update/", UserUpdateAPI.as_view(), name="users-update"),
]

public_patterns = []

urlpatterns = internal_patterns + public_patterns
