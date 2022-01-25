from django.urls import path

from aria.auth.viewsets import (
    AuthLogoutAndBlacklistRefreshTokenForUserAPI,
    AuthTokenObtainAPI,
)
from rest_framework_simplejwt.views import TokenRefreshView


internal_patterns = []

public_patterns = [
    path("tokens/obtain/", AuthTokenObtainAPI.as_view(), name="auth-tokens-obtain"),
    path("tokens/refresh/", TokenRefreshView.as_view(), name="auth-tokens-refresh"),
    path(
        "tokens/blacklist/",
        AuthLogoutAndBlacklistRefreshTokenForUserAPI.as_view(),
        name="auth-tokens-blacklist",
    ),
]

urlpatterns = internal_patterns + public_patterns
