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
from aria.api_auth.exceptions import TokenError
from aria.core.exceptions import ApplicationError

api_private = NinjaAPI(
    title="Aria API Internal",
    renderer=CamelCaseRenderer(),
    parser=CamelCaseParser(),
    auth=JWTAuthRequired(),
)


@api_private.exception_handler(ApplicationError)
def application_error(request: HttpRequest, exc: ApplicationError) -> HttpResponse:
    """
    Exception handler for application errors.
    """

    return application_error_exception_handler(
        api=api_private, request=request, exc=exc
    )


@api_private.exception_handler(NinjaValidationError)
@api_private.exception_handler(PydanticValidationError)
def pydantic_models_validation_error(
    request: HttpRequest, exc: NinjaValidationError | PydanticValidationError
) -> HttpResponse:
    """
    Exception handler for handling schema and record validation errors.
    """

    return pydantic_models_validation_error_exception_handler(
        api=api_private, request=request, exc=exc
    )


@api_private.exception_handler(PermissionDenied)
def permission_denied_error(
    request: HttpRequest, exc: PermissionDenied
) -> HttpResponse:
    """
    Exception handler for permission denied errors.
    """

    return permission_denied_error_exception_handler(
        api=api_private, request=request, exc=exc
    )


# Custom exception handler for PageOutOfBounds errors.
@api_private.exception_handler(PageOutOfBoundsError)
def page_out_of_bounds_error(
    request: HttpRequest, exc: PageOutOfBoundsError
) -> HttpResponse:
    """
    Exception handler for requesting a page that does not exist
    in a paginated response.
    """

    return page_out_of_bounds_error_exception_handler(
        api=api_private, request=request, exc=exc
    )


@api_private.exception_handler(ObjectDoesNotExist)
def object_does_not_exist_error(
    request: HttpRequest, exc: ObjectDoesNotExist
) -> HttpResponse:
    """
    Exception handler for attempting to get an object that does not exist.
    """

    return object_does_not_exist_error_exception_handler(
        api=api_private, request=request, exc=exc
    )


@api_private.exception_handler(ValidationError)
def validation_error(request: HttpRequest, exc: ValidationError) -> HttpResponse:
    """
    Exception handler for when django throws ValidationErrors.
    """

    return validation_error_exception_handler(api=api_private, request=request, exc=exc)


@api_private.exception_handler(TokenError)
def token_error(request: HttpRequest, exc: TokenError) -> HttpResponse:
    """
    Exception handler for token errors.
    """
    return token_error_exception_handler(api=api_private, request=request, exc=exc)
