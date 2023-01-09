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
from aria.api_auth.endpoints import public_endpoints as public_auth_endpoints
from aria.api_auth.exceptions import TokenError
from aria.categories.endpoints import public_endpoints as public_categories_endpoints
from aria.core.endpoints import public_endpoints as public_core_endpoints
from aria.core.exceptions import ApplicationError
from aria.discounts.endpoints import public_endpoints as public_discount_endpoints
from aria.employees.endpoints import public_endpoints as public_employees_endpoints
from aria.forms.endpoints import internal_endpoints as internal_forms_endpoints
from aria.front.endpoints import public_endpoints as public_front_endpoints
from aria.kitchens.endpoints import public_endpoints as public_kitchens_endpoints
from aria.products.endpoints import public_endpoints as public_products_endpoints
from aria.suppliers.endpoints import public_endpoints as public_suppliers_endpoints
from aria.users.endpoints import public_endpoints as public_users_endpoints

#####################
# API configuration #
#####################

api = AriaAPI(
    title="Aria API",
    version="1.0.0",
    urls_namespace="api",
    auth=None,
)

api.add_router("/auth/", public_auth_endpoints)
api.add_router("/categories/", public_categories_endpoints)
api.add_router("/core/", public_core_endpoints)
api.add_router("/discounts/", public_discount_endpoints)
api.add_router("/employees/", public_employees_endpoints)
api.add_router("/forms/", internal_forms_endpoints)
api.add_router("/front/", public_front_endpoints)
api.add_router("/kitchens/", public_kitchens_endpoints)
api.add_router("/products/", public_products_endpoints)
api.add_router("/suppliers/", public_suppliers_endpoints)
api.add_router("/users/", public_users_endpoints)


######################
# Exception handlers #
######################


@api.exception_handler(ApplicationError)
def application_error(request: HttpRequest, exc: ApplicationError) -> HttpResponse:
    """
    Exception handler for application errors.
    """

    return application_error_exception_handler(api=api, request=request, exc=exc)


@api.exception_handler(NinjaValidationError)
@api.exception_handler(PydanticValidationError)
def pydantic_models_validation_error(
    request: HttpRequest, exc: NinjaValidationError | PydanticValidationError
) -> HttpResponse:
    """
    Exception handler for handling schema and record validation errors.
    """

    return pydantic_models_validation_error_exception_handler(
        api=api, request=request, exc=exc
    )


@api.exception_handler(PermissionDenied)
def permission_denied_error(
    request: HttpRequest, exc: PermissionDenied
) -> HttpResponse:
    """
    Exception handler for permission denied errors.
    """

    return permission_denied_error_exception_handler(api=api, request=request, exc=exc)


@api.exception_handler(PageOutOfBoundsError)
def page_out_of_bounds_error(
    request: HttpRequest, exc: PageOutOfBoundsError
) -> HttpResponse:
    """
    Exception handler for requesting a page that does not exist
    in a paginated response.
    """

    return page_out_of_bounds_error_exception_handler(api=api, request=request, exc=exc)


@api.exception_handler(ObjectDoesNotExist)
def object_does_not_exist_error(
    request: HttpRequest, exc: ObjectDoesNotExist
) -> HttpResponse:
    """
    Exception handler for attempting to get an object that does not exist.
    """

    return object_does_not_exist_error_exception_handler(
        api=api, request=request, exc=exc
    )


@api.exception_handler(ValidationError)
def validation_error(request: HttpRequest, exc: ValidationError) -> HttpResponse:
    """
    Exception handler for when django throws ValidationErrors.
    """

    return validation_error_exception_handler(api=api, request=request, exc=exc)


@api.exception_handler(TokenError)
def token_error(request: HttpRequest, exc: TokenError) -> HttpResponse:
    """
    Exception handler for token errors.
    """
    return token_error_exception_handler(api=api, request=request, exc=exc)
