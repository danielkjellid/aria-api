from django.http import HttpRequest, HttpResponse
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response

from rest_framework import status
from rest_framework.permissions import AllowAny

from rest_framework import serializers
from rest_framework.views import APIView


class AuthTokenObtainAPI(TokenObtainPairView):
    """
    [PUBLIC] Viewset for obtaining access and refresh tokens.
    """

    class InputSerializer(TokenObtainPairSerializer):
        default_error_messages = {
            "no_active_account": _(
                "Wrong username or password. Note that you have to separate between lowercase and uppercase characters."
            )
        }

    serializer_class = InputSerializer


class AuthLogoutAndBlacklistRefreshTokenForUserAPI(APIView):
    """
    [PUBLIC] Viewset for blacklisting refresh tokens.
    """

    permission_classes = (AllowAny,)
    authentication_classes = ()

    class InputSerializer(serializers.Serializer):
        refresh_token = serializers.CharField()

    def post(self, request: HttpRequest) -> HttpResponse:
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            refresh_token = serializer.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(
                {"message": _("Successfully logged out."), "data": {}},
                status=status.HTTP_200_OK,
            )
        except RuntimeError:
            return Response(
                {
                    "message": _(
                        "There was a problem logging you out, please try again."
                    ),
                    "data": {},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
