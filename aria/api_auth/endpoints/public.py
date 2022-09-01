from django.http import HttpRequest

from ninja import Router

from aria.api.decorators import api
from aria.api.responses import codes_40x
from aria.api.schemas.responses import ExceptionResponse
from aria.api_auth.exceptions import TokenError
from aria.api_auth.schemas.inputs import (
    TokenBlacklistInput,
    TokensObtainInput,
    TokensRefreshInput,
)
from aria.api_auth.schemas.outputs import TokensObtainOutput, TokensRefreshOutput
from aria.api_auth.services import (
    refresh_token_blacklist,
    token_pair_obtain_for_unauthenticated_user,
    token_pair_obtain_new_from_refresh_token,
)
from aria.core.exceptions import ApplicationError

router = Router(tags=["Auth"])


@api(
    router,
    "tokens/obtain/",
    method="POST",
    response={200: TokensObtainOutput, codes_40x: ExceptionResponse},
    summary="Obtain access and refresh token pair",
)
def auth_obtain_token_pair(
    request: HttpRequest, payload: TokensObtainInput
) -> tuple[int, TokensObtainOutput]:
    """
    Authenticate user credentials and return access and refresh tokens.
    """

    try:
        tokens = token_pair_obtain_for_unauthenticated_user(
            email=payload.email, password=payload.password
        )
    except TokenError as exc:
        raise ApplicationError(
            _("We're unable to log you in, please try again later."), status_code=400
        ) from exc

    return 200, TokensObtainOutput(**tokens.dict())


@api(
    router,
    "tokens/refresh/",
    method="POST",
    response={200: TokensRefreshOutput, codes_40x: ExceptionResponse},
    summary="Obtain a new token pair",
)
def auth_refresh_token_pair(
    request: HttpRequest, payload: TokensRefreshInput
) -> tuple[int, TokensRefreshOutput]:
    """
    Obtain a new token pair based on valid refresh token.
    """

    tokens = token_pair_obtain_new_from_refresh_token(payload.refresh_token)

    return 200, TokensRefreshOutput(**tokens.dict())


@api(
    router,
    "tokens/blacklist/",
    method="POST",
    response={200: None, codes_40x: ExceptionResponse},
    summary="Blacklists a refresh token",
)
def auth_log_out_and_blacklist_refresh_token(
    request: HttpRequest, payload: TokenBlacklistInput
) -> int:
    """
    Blacklists a valid refresh token, typically done when a user logs out.
    """

    refresh_token_blacklist(payload.refresh_token)

    return 200
