from ninja import NinjaAPI
from aria.api.schemas.responses import ExceptionResponse
from aria.api.exceptions import PageOutOfBoundsError
from aria.api_auth.endpoints import public_endpoints as public_auth_endpoints
from aria.api_auth.exceptions import TokenError
from aria.core.exceptions import ApplicationError
from django.core.exceptions import PermissionDenied
from aria.users.endpoints import (
    private_endpoints as private_users_endpoints,
    public_endpoints as public_users_endpoints,
)
from aria.api_auth.authentication import JWTAuthRequired

endpoints = NinjaAPI()

endpoints.add_router(
    "/ninja/auth/", public_auth_endpoints, tags=["[PUBLIC] Auth"], auth=None
)
endpoints.add_router(
    "/users/", public_users_endpoints, tags=["[PUBLIC] Users"], auth=None
)
endpoints.add_router(
    "/users/", private_users_endpoints, tags=["[PRIVATE] Users"], auth=JWTAuthRequired()
)


# Custom exception handler for Application errors.
@endpoints.exception_handler(ApplicationError)
def application_error(request, exc: ApplicationError):
    return endpoints.create_response(
        request,
        ExceptionResponse(message=exc.message, extra=exc.extra),
        status=exc.status_code,
    )


# Custom exception handler for Token errors.
@endpoints.exception_handler(TokenError)
def token_error(request, exc: TokenError):
    return endpoints.create_response(
        request, ExceptionResponse(message=exc.message), status=401
    )


@endpoints.exception_handler(PermissionDenied)
def permission_denied_error(request, exc: PermissionDenied):
    return endpoints.create_response(
        request, ExceptionResponse(message=str(exc)), status=403
    )


# Custom exception handler for PageOutOfBounds errors.
@endpoints.exception_handler(PageOutOfBoundsError)
def page_out_of_bounds_error(request, exc: PageOutOfBoundsError):
    return endpoints.create_response(
        request, ExceptionResponse(message=exc.message), status=404
    )
