from datetime import timedelta

from django.utils import timezone

import jwt
import pytest
from model_bakery import baker

from aria.api_auth.exceptions import TokenError
from aria.api_auth.models import BlacklistedToken, OutstandingToken
from aria.api_auth.selectors import (
    _token_decode,
    access_token_is_valid,
    refresh_token_is_valid,
)
from aria.api_auth.services import _refresh_token_create_and_encode
from aria.api_auth.utils import datetime_to_epoch

pytestmark = pytest.mark.django_db


class TestApiAuthSelectors:
    def test__token_decode(self, refresh_token_payload):
        """
        Test that we're able to decode provided tokens, if it
        has a valid signature.
        """

        user = baker.make("users.User")
        refresh_payload = refresh_token_payload(user_id=user.id)

        invalid_token = jwt.encode(
            refresh_payload, "notvalidsigningkey", algorithm="HS256"
        )

        # Test that we raise an exception when we're unable to decode
        # a token.
        with pytest.raises(TokenError):
            _token_decode(invalid_token)

        valid_token = _refresh_token_create_and_encode(refresh_payload)

        decoded_token = _token_decode(valid_token)

        assert decoded_token is not None
        assert decoded_token.token_type == refresh_payload["token_type"]
        assert decoded_token.exp == datetime_to_epoch(refresh_payload["exp"])
        assert decoded_token.iat == datetime_to_epoch(refresh_payload["iat"])
        assert decoded_token.jti == refresh_payload["jti"]
        assert decoded_token.iss == refresh_payload["iss"]
        assert decoded_token.user_id == user.id

    def test_refresh_token_is_valid(
        self, django_assert_max_num_queries, refresh_token_payload
    ):
        pass

    def test_refresh_token_is_valid_invalid_token_type(
        self, django_assert_max_num_queries, access_token_payload, encode_token
    ):
        """
        Test that the refresh_token_is_valid returns false when the
        token type provided is not refresh.
        """

        refresh_payload = access_token_payload(user_id=1)

        token = encode_token(refresh_payload)

        # Should return before we get to the queries.
        with django_assert_max_num_queries(0):
            is_valid, decoded_token = refresh_token_is_valid(token)

        assert is_valid is False
        assert decoded_token is None

    def test_refresh_token_is_valid_expired_token(
        self, django_assert_max_num_queries, refresh_token_payload, encode_token
    ):
        """
        Test that the refresh_token_is_valid returns false when the
        token provided has expired.
        """

        refresh_payload = refresh_token_payload(user_id=1)
        refresh_payload["exp"] = timezone.now() - timedelta(days=1)

        token = encode_token(refresh_payload)

        # Decoding expired tokens will throw a token error.
        with pytest.raises(TokenError):
            refresh_token_is_valid(token)

    def test_refresh_token_is_valid_invalid_user(
        self, django_assert_max_num_queries, refresh_token_payload, encode_token
    ):
        """
        Test that the refresh_token_is_valid returns false when the
        token provided does not belong to the user.
        """

        user = baker.make("users.User")

        # Create a valid token, and entry in the db with user id.
        refresh_payload = refresh_token_payload(user_id=user.id)
        _refresh_token_create_and_encode(refresh_payload)

        # Create an identical token with the same jti, but with a
        # different user id then the one stored in the db.
        refresh_payload["user_id"] = user.id + 1
        token = encode_token(refresh_payload)

        # Lookup is jti and user id returns a single instance.
        with django_assert_max_num_queries(1):
            is_valid, decoded_token = refresh_token_is_valid(token)

        assert is_valid is False
        assert decoded_token is None

    def test_refresh_token_is_valid_blacklisted(
        self, django_assert_max_num_queries, refresh_token_payload
    ):
        """
        Test that the refresh_token_is_valid returns false when the
        token provided is already blacklisted.
        """

        user = baker.make("users.User")
        refresh_payload = refresh_token_payload(user_id=user.id)

        token = _refresh_token_create_and_encode(refresh_payload)

        # Manually blacklist the recently created token.
        token_instance = OutstandingToken.objects.get(
            jti=refresh_payload["jti"], user_id=user.id
        )
        BlacklistedToken.objects.create(token=token_instance)

        with django_assert_max_num_queries(2):
            is_valid, decoded_token = refresh_token_is_valid(token)

        assert is_valid is False
        assert decoded_token is None

    def test_access_token_is_valid_invalid_token_type(
        self, django_assert_max_num_queries, refresh_token_payload, encode_token
    ):
        """
        Test that the access_token_is_valid returns false when the
        token type provided is not access.
        """

        refresh_payload = refresh_token_payload(user_id=1)
        token = encode_token(refresh_payload)

        with django_assert_max_num_queries(0):
            is_valid, decoded_token = access_token_is_valid(token)

        assert is_valid is False
        assert decoded_token is None

    def test_access_token_is_valid_invalid_expired_token(
        self, django_assert_max_num_queries, access_token_payload, encode_token
    ):
        """
        Test that the refresh_token_is_valid returns false when the
        token provided has expired.
        """

        access_payload = access_token_payload(user_id=1)
        access_payload["exp"] = timezone.now() - timedelta(days=1)

        token = encode_token(access_payload)

        # Decoding expired tokens will throw a token error.
        with pytest.raises(TokenError):
            access_token_is_valid(token)
