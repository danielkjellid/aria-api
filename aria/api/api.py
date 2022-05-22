from django.core.exceptions import PermissionDenied

from ninja import NinjaAPI

from aria.api.exceptions import PageOutOfBoundsError
from aria.api.schemas.responses import ExceptionResponse
from aria.api_auth.authentication import JWTAuthRequired
from aria.api_auth.endpoints import public_endpoints as public_auth_endpoints
from aria.api_auth.exceptions import TokenError
from aria.categories.endpoints import public_endpoints as public_categories_endpoints
from aria.core.exceptions import ApplicationError
from aria.products.endpoints import public_endpoints as public_products_endpoints
from aria.suppliers.endpoints import public_endpoints as public_suppliers_endpoints
from aria.users.endpoints import (
    private_endpoints as private_users_endpoints,
    public_endpoints as public_users_endpoints,
)

api = NinjaAPI(title="Aria API")

# API auth endpoints

api.add_router("/ninja/auth/", public_auth_endpoints, tags=["[PUBLIC] Auth"], auth=None)

# Categories endpoints
api.add_router(
    "/ninja/categories/",
    public_categories_endpoints,
    tags=["[PUBLIC] Categories"],
    auth=None,
)

# Products endpoints
api.add_router(
    "products/", public_products_endpoints, tags=["[PUBLIC] Products"], auth=None
)

# Suppliers endpoints
api.add_router(
    "suppliers/", public_suppliers_endpoints, tags=["[PUBLIC] Suppliers"], auth=None
)

# Users endpoints
api.add_router("/users/", public_users_endpoints, tags=["[PUBLIC] Users"], auth=None)
api.add_router(
    "/users/", private_users_endpoints, tags=["[PRIVATE] Users"], auth=JWTAuthRequired()
)


# Custom exception handler for Application errors.
@api.exception_handler(ApplicationError)
def application_error(request, exc: ApplicationError):
    return api.create_response(
        request,
        ExceptionResponse(message=exc.message, extra=exc.extra),
        status=exc.status_code,
    )


# Custom exception handler for Token errors.
@api.exception_handler(TokenError)
def token_error(request, exc: TokenError):
    return api.create_response(
        request, ExceptionResponse(message=exc.message), status=401
    )


@api.exception_handler(PermissionDenied)
def permission_denied_error(request, exc: PermissionDenied):
    return api.create_response(request, ExceptionResponse(message=str(exc)), status=403)


# Custom exception handler for PageOutOfBounds errors.
@api.exception_handler(PageOutOfBoundsError)
def page_out_of_bounds_error(request, exc: PageOutOfBoundsError):
    return api.create_response(
        request, ExceptionResponse(message=exc.message), status=404
    )
