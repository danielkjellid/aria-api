from ninja import NinjaAPI
from aria.users.viewsets import (
    public_endpoints as public_users_endpoints,
    internal_endpoints as internal_users_endpoints,
)
from aria.core.exceptions import ApplicationError
from aria.api.responses import ExceptionResponse

endpoints = NinjaAPI()

endpoints.add_router("/users/", public_users_endpoints, tags=["[PUBLIC] users"])


# Custom exception handler for Application errors.
@endpoints.exception_handler(ApplicationError)
def application_error(request, exc: ApplicationError):
    return endpoints.create_response(
        request,
        ExceptionResponse(message=exc.message, extra=exc.extra),
        status=exc.status_code,
    )
