from django.utils.translation import gettext as _
import jwt
from django.conf import settings
from aria.api_auth.records import TokenPayload
from aria.api_auth.models import OutstandingToken
from aria.api_auth.exceptions import TokenError
from aria.api_auth.utils import datetime_from_epoch, aware_utcnow

ISSUER = settings.JWT_ISSUER
SIGNING_KEY = settings.JWT_SIGNING_KEY
SIGNING_ALGORITHM = settings.JWT_ALGORITHM


def _token_decode(token: str) -> TokenPayload:
    """
    The most basic decoding and validation. Decodes token, checking
    signature and expiration. Additional checks should be made alongside.
    """

    try:
        decoded_token = jwt.decode(
            token, SIGNING_KEY, algorithms=[SIGNING_ALGORITHM], issuer=ISSUER
        )

        return TokenPayload(
            token_type=decoded_token["token_type"],
            exp=decoded_token["exp"],
            iat=decoded_token["iat"],
            jti=decoded_token["jti"],
            iss=decoded_token["iss"],
            user_id=decoded_token["user_id"],
        )
    except Exception as exc:
        raise TokenError(_(f"Unable to decode provided token: {exc}")) from exc


def refresh_token_is_valid(token: str) -> tuple[bool, TokenPayload | None]:
    """
    Verify the validity of a given refresh token. Cheks
    token expiry, type, if it's blacklisted, it it's issued
    to the right user and if we're able to decode it with
    our secret key.
    """

    try:
        # This throw an exception is we're unable to decode the
        # provided token, we can therefore assume that all token
        # data beyond this point is decoded.
        decoded_token = _token_decode(token)

        token_type = decoded_token.token_type
        token_jti = decoded_token.jti
        token_user_id = decoded_token.user_id

        # Check that we're validating a refresh token type.
        if token_type != "refresh":
            return False, None  # Unexpected token type.

        # Fetch tokens with jti and user id. In theory, this should always
        # be a single instance, but it's easier to filter and check exists,
        # as well as saving queries by selecting related.
        token_bellongs_to_user = OutstandingToken.objects.filter(
            jti=token_jti, user_id=token_user_id
        ).select_related("blacklisted_token")

        # Check that jti matches token issued to user id.
        if not token_bellongs_to_user.exists():
            return False, None  # Provided Token does not belong to issued user.

        # Chekc that token isn't already blacklisted.
        if token_bellongs_to_user[0].blacklisted_token is not None:
            return False, None  # Token is already blacklisted

        # If we've sucessfully decoded token and passed all the checks above,
        # the token is valid.
        return True, decoded_token

    except TokenError as exc:
        raise exc


def access_token_is_valid(token: str) -> tuple[bool, TokenPayload | None]:
    """
    Verify the validity of a given access token. Cheks
    token expiry, type and if we're able to decode it with
    our secret key.
    """

    try:
        decoded_token = _token_decode(token)
        token_type = decoded_token.token_type

        # Check that we're validating a refresh token type.
        if token_type != "access":
            return False, None  # Unexpected token type.

        # If we've sucessfully decoded token and passed all the checks above,
        # the token is valid.
        return True, decoded_token

    except TokenError as exc:
        raise exc
