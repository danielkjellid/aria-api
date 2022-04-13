import pytest
from model_bakery import baker
from rest_framework_simplejwt.tokens import RefreshToken

from aria.auth.viewsets import (
    AuthLogoutAndBlacklistRefreshTokenForUserAPI,
    AuthTokenObtainAPI,
)
from aria.users.models import User


class TestPublicAuthSerializers:
    #####################
    # Input serializers #
    #####################

    @pytest.mark.django_db
    def test_input_serializer_auth_token_obtain(self):
        """
        Test input serializer validity on the AuthTokenObtainAPI
        endpoint.
        """

        user = baker.make(User)
        user.set_password("supersecret")
        user.save()

        payload_json = {"email": user.email, "password": "supersecret"}
        serializer = AuthTokenObtainAPI.InputSerializer(payload_json)

        assert serializer.data

    @pytest.mark.django_db
    def test_input_serializer_auth_token_blacklist(self):
        """
        Test input serializer validity on the
        AuthLogoutAndBlacklistRefreshTokenForUserAPI endpoint.
        """

        user = baker.make(User)
        token = RefreshToken.for_user(user)

        payload_json = {"refresh_token": str(token)}
        serializer = AuthLogoutAndBlacklistRefreshTokenForUserAPI.InputSerializer(
            data=payload_json
        )

        assert serializer.is_valid()
        assert serializer.data
        assert serializer.errors == {}
