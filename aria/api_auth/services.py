from typing import Any, Union
from uuid import uuid4

from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import AbstractBaseUser
from django.utils import timezone
from django.utils.translation import gettext as _

import jwt

from aria.api_auth.exceptions import TokenError
from aria.api_auth.models import BlacklistedToken, OutstandingToken
from aria.api_auth.schemas.records import JWTPair
from aria.api_auth.selectors import refresh_token_is_valid
from aria.core.exceptions import ApplicationError
from aria.users.models import User

ISSUER = settings.JWT_ISSUER
SIGNING_KEY = settings.JWT_SIGNING_KEY
SIGNING_ALGORITHM = settings.JWT_ALGORITHM
ACCESS_TOKEN_LIFESPAN = settings.JWT_ACCESS_TOKEN_LIFETIME
REFRESH_TOKEN_LIFESPAN = settings.JWT_REFRESH_TOKEN_LIFETIME


def _refresh_token_create_and_encode(payload: Any) -> str:
    """
    Encode a refresh token, and store properties in the database.
    """

    refresh_to_expire_at = timezone.now() + REFRESH_TOKEN_LIFESPAN

    # Update payload with token type and expiry.
    payload["token_type"] = "refresh"
    payload["exp"] = refresh_to_expire_at
    payload["jti"] = uuid4().hex

    encoded_refresh_token = jwt.encode(
        payload, SIGNING_KEY, algorithm=SIGNING_ALGORITHM
    )

    OutstandingToken.objects.create(
        user_id=payload["user_id"],
        jti=payload["jti"],
        token=encoded_refresh_token,
        created_at=payload["iat"],
        expires_at=payload["exp"],
    )

    return encoded_refresh_token


def _access_token_create_and_encode(payload: Any) -> str:
    """
    Encode a access token.
    """

    access_to_expire_at = timezone.now() + ACCESS_TOKEN_LIFESPAN

    payload["token_type"] = "access"
    payload["exp"] = access_to_expire_at
    payload["jti"] = uuid4().hex

    encoded_access_token = jwt.encode(payload, SIGNING_KEY, algorithm=SIGNING_ALGORITHM)

    return encoded_access_token


def token_pair_obtain_for_user(user: Union[User, AbstractBaseUser]) -> JWTPair:
    """
    Create a token par of both refresh and access tokens for a
    spcific user.
    """

    payload = {
        "token_type": None,
        "exp": None,
        "iat": timezone.now(),
        "jti": None,
        "iss": ISSUER,
        "user_id": user.pk,
    }

    encoded_refresh_token = _refresh_token_create_and_encode(payload)
    encoded_access_token = _access_token_create_and_encode(payload)

    return JWTPair(
        refresh_token=encoded_refresh_token, access_token=encoded_access_token
    )


def token_pair_obtain_for_unauthenticated_user(email: str, password: str) -> JWTPair:
    """
    Authenticate user credentails and create tokens if
    credentials are valid.
    """

    user = authenticate(username=email, password=password)

    if user is None:
        raise ApplicationError(
            _(
                "Wrong username or password. Note that you have to "
                "separate between lowercase and uppercase characters."
            ),
            status_code=401,
        )

    return token_pair_obtain_for_user(user)


def token_pair_obtain_new_from_refresh_token(token: str) -> JWTPair:
    """
    Invalidates given refresh token, and obtains a new pair of
    refresh and access tokens.
    """

    token_is_valid, token_payload = refresh_token_is_valid(token)

    if not token_is_valid:
        raise TokenError(_("Refresh token provided is invalid."))

    if token_payload is None:
        raise TokenError(_("Token payload is invalid."))

    try:
        user = User.objects.get(id=token_payload.user_id)
    except User.DoesNotExist as exc:
        raise TokenError(_("Issued user in refresh token does not exist.")) from exc

    return token_pair_obtain_for_user(user)


def refresh_token_blacklist(token: str) -> None:
    """
    Adds refresh token to list over blacklisted tokens,
    invalidating it.
    """

    token_is_valid, token_payload = refresh_token_is_valid(token)

    if not token_is_valid:
        raise TokenError(_("Refresh token provided is invalid."))

    if token_payload is None:
        raise TokenError(_("Token payload is invalid."))

    try:
        token_instance = OutstandingToken.objects.get(
            jti=token_payload.jti, user_id=token_payload.user_id
        )
        BlacklistedToken.objects.create(token=token_instance)
    except OutstandingToken.DoesNotExist as exc:
        raise TokenError(_("Refresh token provided does not exist.")) from exc
