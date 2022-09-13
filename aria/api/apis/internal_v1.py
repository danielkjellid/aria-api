from django.contrib.admin.views.decorators import staff_member_required
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
from aria.api_auth.authentication import JWTAuthRequired
from aria.api_auth.exceptions import TokenError
from aria.core.exceptions import ApplicationError
from aria.notes.endpoints import internal_endpoints as notes_endpoints
from aria.users.endpoints import internal_endpoints as users_endpoints

api_internal = AriaAPI(
    title="Aria Internal API",
    urls_namespace="api-internal",
    version="1.0.0",
    auth=JWTAuthRequired(),
    docs_decorator=staff_member_required,
)

# Notes endpoints
api_internal.add_router("/notes/", notes_endpoints)

# Users endpoints
api_internal.add_router("/users/", users_endpoints)


@api_internal.exception_handler(ApplicationError)
def application_error(request: HttpRequest, exc: ApplicationError) -> HttpResponse:
    """
    Exception handler for application errors.
    """

    return application_error_exception_handler(
        api=api_internal, request=request, exc=exc
    )


@api_internal.exception_handler(NinjaValidationError)
@api_internal.exception_handler(PydanticValidationError)
def pydantic_models_validation_error(
    request: HttpRequest, exc: NinjaValidationError | PydanticValidationError
) -> HttpResponse:
    """
    Exception handler for handling schema and record validation errors.
    """

    return pydantic_models_validation_error_exception_handler(
        api=api_internal, request=request, exc=exc
    )


@api_internal.exception_handler(PermissionDenied)
def permission_denied_error(
    request: HttpRequest, exc: PermissionDenied
) -> HttpResponse:
    """
    Exception handler for permission denied errors.
    """

    return permission_denied_error_exception_handler(
        api=api_internal, request=request, exc=exc
    )


# Custom exception handler for PageOutOfBounds errors.
@api_internal.exception_handler(PageOutOfBoundsError)
def page_out_of_bounds_error(
    request: HttpRequest, exc: PageOutOfBoundsError
) -> HttpResponse:
    """
    Exception handler for requesting a page that does not exist
    in a paginated response.
    """

    return page_out_of_bounds_error_exception_handler(
        api=api_internal, request=request, exc=exc
    )


@api_internal.exception_handler(ObjectDoesNotExist)
def object_does_not_exist_error(
    request: HttpRequest, exc: ObjectDoesNotExist
) -> HttpResponse:
    """
    Exception handler for attempting to get an object that does not exist.
    """

    return object_does_not_exist_error_exception_handler(
        api=api_internal, request=request, exc=exc
    )


@api_internal.exception_handler(ValidationError)
def validation_error(request: HttpRequest, exc: ValidationError) -> HttpResponse:
    """
    Exception handler for when django throws ValidationErrors.
    """

    return validation_error_exception_handler(
        api=api_internal, request=request, exc=exc
    )


@api_internal.exception_handler(TokenError)
def token_error(request: HttpRequest, exc: TokenError) -> HttpResponse:
    """
    Exception handler for token errors.
    """
    return token_error_exception_handler(api=api_internal, request=request, exc=exc)
