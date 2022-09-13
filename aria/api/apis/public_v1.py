from django.core.exceptions import ObjectDoesNotExist, PermissionDenied, ValidationError
from django.http import HttpRequest, HttpResponse

from ninja.errors import ValidationError as NinjaValidationError
from pydantic.error_wrappers import ValidationError as PydanticValidationError

from aria.api.base import AriaAPI
from aria.api.exception_handlers import (
    application_error_exception_handler,
    object_does_not_exist_error_exception_handler,
    page_out_of_bounds_error_exception_handler,
    permission_denied_error_exception_handler,
    pydantic_models_validation_error_exception_handler,
    token_error_exception_handler,
    validation_error_exception_handler,
)
from aria.api.exceptions import PageOutOfBoundsError
from aria.api_auth.endpoints import public_endpoints as auth_endpoints
from aria.api_auth.exceptions import TokenError
from aria.categories.endpoints import public_endpoints as categories_endpoints
from aria.core.endpoints import public_endpoints as core_endpoints
from aria.core.exceptions import ApplicationError
from aria.discounts.endpoints import public_endpoints as discount_endpoints
from aria.employees.endpoints import public_endpoints as employees_endpoints
from aria.front.endpoints import public_endpoints as front_endpoints
from aria.kitchens.endpoints import public_endpoints as kitchens_endpoints
from aria.products.endpoints import public_endpoints as products_endpoints
from aria.suppliers.endpoints import public_endpoints as suppliers_endpoints
from aria.users.endpoints import public_endpoints as users_endpoints

api_public = AriaAPI(
    title="Aria Public API",
    urls_namespace="api-public",
    version="1.0.0",
    auth=None,
    docs_decorator=None,
)

# API auth endpoints
api_public.add_router("/auth/", auth_endpoints)

# Categories endpoints
api_public.add_router("/categories/", categories_endpoints)

# Core endpoints
api_public.add_router("/core/", core_endpoints)

# Discount endpoints
api_public.add_router("/discounts/", discount_endpoints)

# Employees endpoints
api_public.add_router("/employees/", employees_endpoints)

# Front endpoints
api_public.add_router("/front/", front_endpoints)

# Kitchens endpoints
api_public.add_router("/kitchens/", kitchens_endpoints)

# Products endpoints
api_public.add_router("/products/", products_endpoints)

# Suppliers endpoints
api_public.add_router("/suppliers/", suppliers_endpoints)

# Users endpoints
api_public.add_router("/users/", users_endpoints)


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
