from django.urls import path

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from aria.core.viewsets import (
    LogoutAndBlacklistRefreshTokenForUserView,
    MyTokenObtainPairView,
)

urlpatterns = [
    # endpoint for obtaining token, takes email and password as payload
    path("token/obtain/", MyTokenObtainPairView.as_view(), name="token-create"),
    # endpoint for refreshing tokens, takes refrest_token as payload
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    # endpoint for blacklisting used tokens
    path(
        "token/blacklist/",
        LogoutAndBlacklistRefreshTokenForUserView.as_view(),
        name="token-blacklist",
    ),
]
