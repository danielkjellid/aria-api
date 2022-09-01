from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse

from ninja import NinjaAPI
from ninja.errors import ValidationError as NinjaValidationError

from aria.api.exceptions import PageOutOfBoundsError
from aria.api.parsers import CamelCaseParser, ORJSONParser
from aria.api.renderers import CamelCaseRenderer, ORJSONRenderer
from aria.api.schemas.responses import ExceptionResponse
from aria.api.utils import translate_pydantic_validation_messages
from aria.api_auth.authentication import JWTAuthRequired
from aria.api_auth.endpoints import public_endpoints as public_auth_endpoints
from aria.api_auth.exceptions import TokenError
from aria.categories.endpoints import public_endpoints as public_categories_endpoints
from aria.core.endpoints import public_endpoints as public_core_endpoints
from aria.core.exceptions import ApplicationError
from aria.core.humps import camelize
from aria.discounts.endpoints import public_endpoints as public_discount_endpoints
from aria.employees.endpoints import public_endpoints as public_employees_endpoints
from aria.front.endpoints import public_endpoints as public_front_endpoints
from aria.kitchens.endpoints import public_endpoints as public_kitchens_endpoints
from aria.notes.endpoints import private_endpoints as private_notes_endpoints
from aria.products.endpoints import public_endpoints as public_products_endpoints
from aria.suppliers.endpoints import public_endpoints as public_suppliers_endpoints
from aria.users.endpoints import (
    private_endpoints as private_users_endpoints,
    public_endpoints as public_users_endpoints,
)

# Temporary: the new frontend app expects output in camelcase.
if settings.CAMEL_CASE_RENDERER:
    api = NinjaAPI(
        title="Aria API",
        renderer=CamelCaseRenderer(),
        parser=CamelCaseParser(),
    )
else:
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

# Discount endpoints
api.add_router("/discounts/", public_discount_endpoints, auth=None)

# Employees endpoints
api.add_router("/employees/", public_employees_endpoints, auth=None)

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


@api.exception_handler(ApplicationError)
def application_error(request: HttpRequest, exc: ApplicationError) -> HttpResponse:
    """
    Exception handler for application errors.
    """
    print(exc.message)

    return api.create_response(
        request,
        ExceptionResponse(message=exc.message, extra=exc.extra).dict(),
        status=exc.status_code,
    )


@api.exception_handler(NinjaValidationError)
def pydantic_validation_error(
    request: HttpRequest, exc: NinjaValidationError
) -> HttpResponse:
    """
    Exception handler for handling schema and record validation errors.
    """

    locale = request.META.get("HTTP_ACCEPT_LANGUAGE", "en")
    errors = translate_pydantic_validation_messages(errors=exc.errors, locale=locale)

    field_errors = {}

    for error in errors:
        location = error["loc"]
        field = camelize(location[len(location) - 1])
        field_errors[field] = error["msg"]

    return api.create_response(
        request,
        ExceptionResponse(message="Something went wrong.", extra=field_errors).dict(),
        status=400,
    )


@api.exception_handler(TokenError)
def token_error(request: HttpRequest, exc: TokenError) -> HttpResponse:
    """
    Exception handler for token errors.
    """
    return api.create_response(
        request, ExceptionResponse(message=exc.message).dict(), status=401
    )


@api.exception_handler(PermissionDenied)
def permission_denied_error(
    request: HttpRequest, exc: PermissionDenied
) -> HttpResponse:
    """
    Exception handler for permission denied errors.
    """
    return api.create_response(
        request, ExceptionResponse(message=str(exc)).dict(), status=403
    )


# Custom exception handler for PageOutOfBounds errors.
@api.exception_handler(PageOutOfBoundsError)
def page_out_of_bounds_error(
    request: HttpRequest, exc: PageOutOfBoundsError
) -> HttpResponse:
    """
    Exception handler for requesting a page that does not exist
    in a paginated response.
    """
    return api.create_response(
        request, ExceptionResponse(message=exc.message).dict(), status=404
    )
