from django.utils.translation import gettext as _

from ninja import Router

from aria.api.decorators import api
from aria.api.responses import codes_40x
from aria.api.schemas.responses import ExceptionResponse, GenericResponse
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

router = Router(tags="auth")


@api(
    router,
    "tokens/obtain/",
    method="POST",
    response={200: GenericResponse, codes_40x: ExceptionResponse},
    summary="Obtain access and refresh token pair",
    description="Authenticate user credentials and return access and refresh tokens.",
)
def auth_obtain_token_pair(request, payload: TokensObtainInput):
    tokens = token_pair_obtain_for_unauthenticated_user(
        email=payload.email, password=payload.password
    )

    return 200, GenericResponse(
        message=_("Sucessfully logged in."),
        data=TokensObtainOutput(**tokens.dict()),
    )


@api(
    router,
    "tokens/refresh/",
    method="POST",
    response={200: GenericResponse, codes_40x: ExceptionResponse},
    summary="Obtain a new token pair",
    description="Obtain a new token pair based on valid refresh token.",
)
def auth_refresh_token_pair(request, payload: TokensRefreshInput):
    tokens = token_pair_obtain_new_from_refresh_token(payload.refresh_token)

    return 200, GenericResponse(
        message=_("Tokens sucessfully refreshed."),
        data=TokensRefreshOutput(**tokens.dict()),
    )


@api(
    router,
    "tokens/blacklist/",
    method="POST",
    response={200: GenericResponse, codes_40x: ExceptionResponse},
    summary="Blacklists a refresh token",
    description="Blacklists a valid refresh token, typically done when a user logs out.",
)
def auth_log_out_and_blacklist_refresh_token(request, payload: TokenBlacklistInput):
    refresh_token_blacklist(payload.refresh_token)

    return 200, GenericResponse(
        message=_("Refresh token sucessfully blacklisted."), data={}
    )
