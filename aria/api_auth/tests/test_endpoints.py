import pytest
from aria.api_auth.services import _refresh_token_create_and_encode
import json
from aria.api_auth.models import BlacklistedToken
import jwt

pytestmark = pytest.mark.django_db


class TestAPIAuthPublicEndpoints:

    BASE_ENDPOINT = (
        "/api/ninja/auth"  # TODO: Remove /ninja/ when drf migration is done.
    )

    def test_auth_obtain_token_pair(
        self,
        anonymous_client,
        django_assert_max_num_queries,
        unprivileged_user,
    ):
        """
        Test obtaining tokens from endpoint.
        """

        user = unprivileged_user
        user.set_password("supersecret1234")
        user.save()

        # Getting user (1) and site (2) takes 3 queries.
        with django_assert_max_num_queries(3):
            failed_response = anonymous_client.post(
                f"{self.BASE_ENDPOINT}/tokens/obtain/",
                data={
                    "email": "testuser@example.com",
                    "password": "nottherightpassword",
                },
                content_type="application/json",
            )

        assert failed_response.status_code == 401

        # Getting user (1) and site (2) and creating refresh token (1)
        # takes 4 queries.
        with django_assert_max_num_queries(4):
            response = anonymous_client.post(
                f"{self.BASE_ENDPOINT}/tokens/obtain/",
                data={"email": "testuser@example.com", "password": "supersecret1234"},
                content_type="application/json",
            )

        # Assert that we return a valid response.
        assert response.status_code == 200
        assert list(json.loads(response.content)["data"].keys())[0] == "refresh_token"
        assert list(json.loads(response.content)["data"].keys())[1] == "access_token"

    def test_auth_refresh_token_pair(
        self,
        anonymous_client,
        django_assert_max_num_queries,
        refresh_token_payload,
        encode_token,
        unprivileged_user,
    ):
        """
        Test obtaining a new token pair by using a valid refresh token.
        """

        user = unprivileged_user

        refresh_payload = refresh_token_payload(user_id=user.id + 1)
        invalid_refresh_token = encode_token(refresh_payload)

        # Should not use any queries as token signature is invalid,
        # so service returns before reaching the queries.
        with django_assert_max_num_queries(1):
            failed_response = anonymous_client.post(
                f"{self.BASE_ENDPOINT}/tokens/refresh/",
                data={"refresh_token": invalid_refresh_token},
                content_type="application/json",
            )

        assert failed_response.status_code == 401

        refresh_payload["user_id"] = user.id
        valid_refresh_token = _refresh_token_create_and_encode(refresh_payload)

        # Check if refresh token exist (1), if its blacklisted (1), get user
        # based on token user_id (1) and create new refresh (1). Uses 4 queries.
        with django_assert_max_num_queries(4):
            response = anonymous_client.post(
                f"{self.BASE_ENDPOINT}/tokens/refresh/",
                data={"refresh_token": valid_refresh_token},
                content_type="application/json",
            )

        # Assert that we return a valid response.
        assert response.status_code == 200
        assert list(json.loads(response.content)["data"].keys())[0] == "refresh_token"
        assert list(json.loads(response.content)["data"].keys())[1] == "access_token"

    def test_auth_log_out_and_blacklist_refresh_token(
        self,
        anonymous_client,
        django_assert_max_num_queries,
        refresh_token_payload,
        unprivileged_user,
        decode_token,
    ):
        """
        Test blackliting a provided valid token.
        """

        user = unprivileged_user

        refresh_payload = refresh_token_payload(user_id=user.id)
        invalid_refresh_token = jwt.encode(
            refresh_payload, "notvalidsigningkey", algorithm="HS256"
        )

        # Should not use any queries as token signature is invalid,
        # so service returns before reaching the queries.
        with django_assert_max_num_queries(0):
            failed_response = anonymous_client.post(
                f"{self.BASE_ENDPOINT}/tokens/blacklist/",
                data={"refresh_token": invalid_refresh_token},
                content_type="application/json",
            )

        assert failed_response.status_code == 401

        valid_refresh_token = _refresh_token_create_and_encode(refresh_payload)

        assert BlacklistedToken.objects.all().count() == 0

        # Used 4 queries: checking if token belongs to user (1) and
        # if it's blacklisted (1), then getting the token (1) and
        # add it to the blacklist (1).
        with django_assert_max_num_queries(4):
            response = anonymous_client.post(
                f"{self.BASE_ENDPOINT}/tokens/blacklist/",
                data={"refresh_token": valid_refresh_token},
                content_type="application/json",
            )

        decoded_token = decode_token(valid_refresh_token)
        blacklisted_token = BlacklistedToken.objects.filter(
            token__jti=decoded_token["jti"], token__user_id=decoded_token["user_id"]
        )

        # Assert that we return a valid response.
        assert response.status_code == 200
        assert blacklisted_token.exists()
        assert blacklisted_token.count() == 1