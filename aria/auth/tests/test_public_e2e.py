import json
import pytest

from model_bakery import baker

from aria.users.models import User
from aria.users.tests.conftest import unauthenticated_client

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError


unauthenticated_client = unauthenticated_client

pytestmark = pytest.mark.django_db


class TestPublicAuthEndpoints:

    base_endpoint = "/api/auth"

    def test_unauthenticated_token_obtain(
        self, unauthenticated_client, django_assert_max_num_queries
    ):
        """
        Test obtaining a token pair from the obtain endpoint.
        """

        user = baker.make(User)
        user.set_password("supersecret")
        user.save()

        payload_json = {"email": user.email, "password": "supersecret"}

        url = f"{self.base_endpoint}/tokens/obtain/"

        # Get user (1) and create token (1)
        with django_assert_max_num_queries(2):
            response = unauthenticated_client.post(
                url, data=payload_json, format="json"
            )

        returned_refresh = json.loads(response.content)["refresh"]
        returned_access = json.loads(response.content)["access"]
        token = RefreshToken(returned_refresh)

        assert response.status_code == 200
        assert returned_refresh
        assert returned_access

        # Assert that refresh_token returned is not blacklisted
        assert token.check_blacklist() == None

    def test_unauthenticated_token_refresh(
        self, unauthenticated_client, django_assert_max_num_queries
    ):
        """
        Test refreshing a new token pair from the refresh
        endpoint.
        """

        user = baker.make(User)
        token = RefreshToken.for_user(user)

        payload_json = {"refresh": str(token), "access": str(token.access_token)}

        url = f"{self.base_endpoint}/tokens/refresh/"

        with django_assert_max_num_queries(6):
            response = unauthenticated_client.post(
                url, data=payload_json, format="json"
            )

        assert response.status_code == 200
        assert json.loads(response.content)["refresh"]
        assert json.loads(response.content)["access"]

    def test_unauthenticated_token_blacklist(
        self, unauthenticated_client, django_assert_max_num_queries
    ):
        """
        Test refreshing a new token pair from the refresh
        endpoint.
        """

        user = baker.make(User)
        token = RefreshToken.for_user(user)

        payload_json = {"refresh_token": str(token)}

        url = f"{self.base_endpoint}/tokens/blacklist/"

        with django_assert_max_num_queries(6):
            response = unauthenticated_client.post(
                url, data=payload_json, format="json"
            )

        assert response.status_code == 200

        # Check that token is actually blacklisted, simplejwts
        # check_blacklist is retarded and raises an exception
        # instead og just retruning true / false.
        with pytest.raises(TokenError):
            token.check_blacklist()
