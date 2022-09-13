from django.core.exceptions import ObjectDoesNotExist, PermissionDenied, ValidationError
from django.http import HttpRequest, HttpResponse
from ninja import NinjaAPI
from ninja.errors import ValidationError as NinjaValidationError
from pydantic.error_wrappers import ValidationError as PydanticValidationError

from aria.api.exception_handlers import (
    application_error_exception_handler,
    pydantic_models_validation_error_exception_handler,
    permission_denied_error_exception_handler,
    page_out_of_bounds_error_exception_handler,
    object_does_not_exist_error_exception_handler,
    validation_error_exception_handler,
    token_error_exception_handler,
)
from aria.api.exceptions import PageOutOfBoundsError
from aria.api.parsers import CamelCaseParser
from aria.api.renderers import CamelCaseRenderer
from aria.api_auth.authentication import JWTAuthRequired
from aria.api_auth.endpoints import public_endpoints as public_auth_endpoints
from aria.api_auth.exceptions import TokenError
from aria.categories.endpoints import public_endpoints as public_categories_endpoints
from aria.core.endpoints import public_endpoints as public_core_endpoints
from aria.core.exceptions import ApplicationError
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

api_public = NinjaAPI(
    title="Aria API Public",
    renderer=CamelCaseRenderer(),
    parser=CamelCaseParser(),
    auth=None,
)


# API auth endpoints

api_public.add_router("/auth/", public_auth_endpoints, auth=None)

# Categories endpoints
api_public.add_router("/categories/", public_categories_endpoints, auth=None)

# Core endpoints
api_public.add_router("/core/", public_core_endpoints, auth=None)

# Discount endpoints
api_public.add_router("/discounts/", public_discount_endpoints, auth=None)

# Employees endpoints
api_public.add_router("/employees/", public_employees_endpoints, auth=None)

# Front endpoints
api_public.add_router("/front/", public_front_endpoints, auth=None)

# Kitchens endpoints
api_public.add_router("/kitchens/", public_kitchens_endpoints, auth=None)

# Notes endpoints
api_public.add_router("/notes/", private_notes_endpoints, auth=JWTAuthRequired())

# Products endpoints
api_public.add_router("/products/", public_products_endpoints, auth=None)

# Suppliers endpoints
api_public.add_router("/suppliers/", public_suppliers_endpoints, auth=None)

# Users endpoints
api_public.add_router("/users/", private_users_endpoints, auth=JWTAuthRequired())
api_public.add_router("/users/", public_users_endpoints, auth=None)


@api_public.exception_handler(ApplicationError)
def application_error(request: HttpRequest, exc: ApplicationError) -> HttpResponse:
    """
    Exception handler for application errors.
    """

    return application_error_exception_handler(api=api_public, request=request, exc=exc)


@api_public.exception_handler(NinjaValidationError)
@api_public.exception_handler(PydanticValidationError)
def pydantic_models_validation_error(
    request: HttpRequest, exc: NinjaValidationError | PydanticValidationError
) -> HttpResponse:
    """
    Exception handler for handling schema and record validation errors.
    """

    return pydantic_models_validation_error_exception_handler(
        api=api_public, request=request, exc=exc
    )


@api_public.exception_handler(PermissionDenied)
def permission_denied_error(
    request: HttpRequest, exc: PermissionDenied
) -> HttpResponse:
    """
    Exception handler for permission denied errors.
    """

    return permission_denied_error_exception_handler(
        api=api_public, request=request, exc=exc
    )


# Custom exception handler for PageOutOfBounds errors.
@api_public.exception_handler(PageOutOfBoundsError)
def page_out_of_bounds_error(
    request: HttpRequest, exc: PageOutOfBoundsError
) -> HttpResponse:
    """
    Exception handler for requesting a page that does not exist
    in a paginated response.
    """

    return page_out_of_bounds_error_exception_handler(
        api=api_public, request=request, exc=exc
    )


@api_public.exception_handler(ObjectDoesNotExist)
def object_does_not_exist_error(
    request: HttpRequest, exc: ObjectDoesNotExist
) -> HttpResponse:
    """
    Exception handler for attempting to get an object that does not exist.
    """

    return object_does_not_exist_error_exception_handler(
        api=api_public, request=request, exc=exc
    )


@api_public.exception_handler(ValidationError)
def validation_error(request: HttpRequest, exc: ValidationError) -> HttpResponse:
    """
    Exception handler for when django throws ValidationErrors.
    """

    return validation_error_exception_handler(api=api_public, request=request, exc=exc)


@api_public.exception_handler(TokenError)
def token_error(request: HttpRequest, exc: TokenError) -> HttpResponse:
    """
    Exception handler for token errors.
    """
    return token_error_exception_handler(api=api_public, request=request, exc=exc)
