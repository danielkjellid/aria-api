from typing import Any

from django.core.exceptions import ObjectDoesNotExist, PermissionDenied, ValidationError
from django.http import HttpRequest, HttpResponse
from django.utils.translation import activate, deactivate, gettext as _

from ninja import NinjaAPI
from ninja.errors import ValidationError as NinjaValidationError
from pydantic.error_wrappers import ValidationError as PydanticValidationError

from aria.api.exceptions import PageOutOfBoundsError
from aria.api.schemas.responses import ExceptionResponse
from aria.api.utils import translate_pydantic_validation_messages
from aria.api_auth.exceptions import TokenError
from aria.core.exceptions import ApplicationError
from aria.core.humps import camelize


def application_error_exception_handler(
    *, api: NinjaAPI, request: HttpRequest, exc: ApplicationError
) -> HttpResponse:
    """
    Exception handler for application errors.
    """

    return api.create_response(
        request,
        ExceptionResponse(message=exc.message, extra=exc.extra).dict(),
        status=exc.status_code,
    )


def pydantic_models_validation_error_exception_handler(
    *,
    api: NinjaAPI,
    request: HttpRequest,
    exc: NinjaValidationError | PydanticValidationError,
) -> HttpResponse:
    """
    Exception handler for handling schema and record validation errors.
    """

    locale = request.META.get("HTTP_ACCEPT_LANGUAGE", "en")
    errors = translate_pydantic_validation_messages(  # type: ignore # pylint: disable=line-too-long
        errors=exc.errors, locale=locale
    )

    field_errors: dict[str, Any] = {}

    for error in errors:
        location = error["loc"]
        field = camelize(location[len(location) - 1])
        field_errors[field] = error["msg"]  # type: ignore

    activate(locale)
    message = _("There were errors in the form. Please correct them and try again.")
    deactivate()

    return api.create_response(
        request,
        ExceptionResponse(
            message=message,
            extra=field_errors,
        ).dict(),
        status=400,
    )


def permission_denied_error_exception_handler(
    *, api: NinjaAPI, request: HttpRequest, exc: PermissionDenied
) -> HttpResponse:
    """
    Exception handler for permission denied errors.
    """

    return api.create_response(
        request, ExceptionResponse(message=str(exc)).dict(), status=403
    )


def page_out_of_bounds_error_exception_handler(
    *, api: NinjaAPI, request: HttpRequest, exc: PageOutOfBoundsError
) -> HttpResponse:
    """
    Exception handler for requesting a page that does not exist
    in a paginated response.
    """

    return api.create_response(
        request, ExceptionResponse(message=exc.message).dict(), status=404
    )


def object_does_not_exist_error_exception_handler(
    *, api: NinjaAPI, request: HttpRequest, exc: ObjectDoesNotExist
) -> HttpResponse:
    """
    Exception handler for attempting to get an object that does not exist.
    """

    return api.create_response(
        request, ExceptionResponse(message=str(exc)).dict(), status=400
    )


def validation_error_exception_handler(  # pylint: disable=unused-argument
    *, api: NinjaAPI, request: HttpRequest, exc: ValidationError
) -> HttpResponse:
    locale = request.META.get("HTTP_ACCEPT_LANGUAGE", "en")

    activate(locale)
    message = _("Something went wrong. Please double check the form and try again.")
    deactivate()

    return api.create_response(
        request, ExceptionResponse(message=message).dict(), status=400
    )


def token_error_exception_handler(
    *, api: NinjaAPI, request: HttpRequest, exc: TokenError
) -> HttpResponse:
    """
    Exception handler for token errors.
    """

    return api.create_response(
        request, ExceptionResponse(message=exc.message), status=401
    )
