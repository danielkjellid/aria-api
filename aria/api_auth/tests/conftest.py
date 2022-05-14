from datetime import datetime, timedelta
from uuid import uuid4

from django.conf import settings
from django.utils import timezone

import jwt
import pytest

from aria.api_auth.records import JWTPair


@pytest.fixture
def token_payload():
    def _create_payload(
        token_type: str,
        exp: datetime | None = None,
        jti: str | None = None,
        user_id: int = 1,
    ):
        if exp is None:
            exp = timezone.now() + timedelta(days=14)

        if jti is None:
            jti = uuid4().hex

        return {
            "token_type": token_type,
            "exp": exp,
            "iat": timezone.now(),
            "jti": jti,
            "iss": "api.flis.no",
            "user_id": user_id,
        }

    return _create_payload


@pytest.fixture
def refresh_token_payload(token_payload):
    def _create_refresh_payload(
        exp: datetime | None = None,
        jti: str | None = None,
        user_id: int = 1,
    ):
        return token_payload("refresh", exp=exp, jti=jti, user_id=user_id)

    return _create_refresh_payload


@pytest.fixture
def access_token_payload(token_payload):
    def _create_access_payload(
        exp: datetime | None = None,
        jti: str | None = None,
        user_id: int = 1,
    ):
        return token_payload("access", exp=exp, jti=jti, user_id=user_id)

    return _create_access_payload


@pytest.fixture
def encode_token():
    """
    Encode raw token payload input without any validation.
    """

    def _encode_token(payload: dict[str, str | int | datetime]):
        encoded_token = jwt.encode(
            payload, settings.JWT_SIGNING_KEY, algorithm=settings.JWT_ALGORITHM
        )
        return encoded_token

    return _encode_token


@pytest.fixture
def decode_token():
    """
    Encode raw token payload input without any validation.
    """

    def _decode_token(token: str):
        decoded_token = jwt.decode(
            token, settings.JWT_SIGNING_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        return decoded_token

    return _decode_token


@pytest.fixture
def token_pair(refresh_token_payload, access_token_payload, encode_token):
    """
    A simple object with created valid tokens.
    """

    def _create_token_pair(user_id: int):
        refresh_token = encode_token(refresh_token_payload(user_id=user_id))
        access_token = encode_token(access_token_payload(user_id=user_id))

        return JWTPair(access_token=access_token, refresh_token=refresh_token)

    return _create_token_pair
