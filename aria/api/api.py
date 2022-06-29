from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse

from ninja import NinjaAPI

from aria.api.exceptions import PageOutOfBoundsError
from aria.api.parsers import ORJSONParser
from aria.api.renderers import ORJSONRenderer
from aria.api.schemas.responses import ExceptionResponse
from aria.api_auth.authentication import JWTAuthRequired
from aria.api_auth.endpoints import public_endpoints as public_auth_endpoints
from aria.api_auth.exceptions import TokenError
from aria.categories.endpoints import public_endpoints as public_categories_endpoints
from aria.core.endpoints import public_endpoints as public_core_endpoints
from aria.core.exceptions import ApplicationError
from aria.front.endpoints import public_endpoints as public_front_endpoints
from aria.kitchens.endpoints import public_endpoints as public_kitchens_endpoints
from aria.notes.endpoints import private_endpoints as private_notes_endpoints
from aria.products.endpoints import public_endpoints as public_products_endpoints
from aria.suppliers.endpoints import public_endpoints as public_suppliers_endpoints
from aria.users.endpoints import (
    private_endpoints as private_users_endpoints,
    public_endpoints as public_users_endpoints,
)

api = NinjaAPI(
    title="Aria API",
    renderer=ORJSONRenderer(),
    parser=ORJSONParser(),
)

# API auth endpoints

api.add_router("/auth/", public_auth_endpoints, auth=None)

# Categories endpoints
api.add_router("/categories/", public_categories_endpoints, auth=None)

# Core endpoints
api.add_router("/core/", public_core_endpoints, auth=None)

# Front endpoints
api.add_router("/front/", public_front_endpoints, auth=None)

# Kitchens endpoints
api.add_router("/kitchens/", public_kitchens_endpoints, auth=None)

# Notes endpoints
api.add_router("/notes/", private_notes_endpoints, auth=JWTAuthRequired())

# Products endpoints
api.add_router("/products/", public_products_endpoints, auth=None)

# Suppliers endpoints
api.add_router("/suppliers/", public_suppliers_endpoints, auth=None)

# Users endpoints
api.add_router("/users/", private_users_endpoints, auth=JWTAuthRequired())
api.add_router("/users/", public_users_endpoints, auth=None)


# Custom exception handler for Application errors.
@api.exception_handler(ApplicationError)
def application_error(request: HttpRequest, exc: ApplicationError) -> HttpResponse:
    return api.create_response(
        request,
        ExceptionResponse(message=exc.message, extra=exc.extra),
        status=exc.status_code,
    )


# Custom exception handler for Token errors.
@api.exception_handler(TokenError)
def token_error(request: HttpRequest, exc: TokenError) -> HttpResponse:
    return api.create_response(
        request, ExceptionResponse(message=exc.message), status=401
    )


@api.exception_handler(PermissionDenied)
def permission_denied_error(
    request: HttpRequest, exc: PermissionDenied
) -> HttpResponse:
    return api.create_response(request, ExceptionResponse(message=str(exc)), status=403)


# Custom exception handler for PageOutOfBounds errors.
@api.exception_handler(PageOutOfBoundsError)
def page_out_of_bounds_error(
    request: HttpRequest, exc: PageOutOfBoundsError
) -> HttpResponse:
    return api.create_response(
        request, ExceptionResponse(message=exc.message), status=404
    )
