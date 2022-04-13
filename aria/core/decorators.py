from django.conf import settings
from typing import Callable, Any, TypeVar
from aria.core.permissions import HasUserOrGroupPermission
from rest_framework.permissions import IsAdminUser, AllowAny
from aria.core.schemas import APIViewSchema


F = TypeVar("F", bound=Callable[..., Any])


class NotAllowedInProductionException(Exception):
    pass


def not_in_production(func):
    """
    Decorator that raises exception if run in production.
    Typically used for management commands that changes production data.
    """

    def decorator(*args, **kwargs):
        if settings.PRODUCTION or settings.ENVIRONMENT == "prod":
            raise NotAllowedInProductionException(
                "This operation is not allowed in production!"
            )

        return func(*args, **kwargs)

    return decorator


def required_method_permissions(permissions: dict[str, list[str]]) -> Callable[[F], F]:
    """
    Decorator that add specific permissions needed to visit an
    endpoint. For example:

    @required_method_permissions({
        "GET": ["some_permission],
        "POST": ["some_other_permision],
    })
    """

    def decorator(viewset):
        viewset.permission_classes += (HasUserOrGroupPermission,)
        viewset.required_permissions = permissions

    return decorator


def public_endpoint(func):
    """
    Decorator that sets a endpoint as publicly available.
    """

    def decorator(viewset):
        viewset.permission_classes = (AllowAny,)
        viewset.authentication_classes = ()
        viewset.schema = APIViewSchema()

    return decorator


def internal_endpoint(func):
    """
    Decorator that sets endpoint as internal, e.g. for
    users that have is_staff = True.
    """

    def decorator(viewset):
        viewset.permission_classes += (IsAdminUser,)
        viewset.schema = APIViewSchema

    return decorator
