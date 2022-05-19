from django.conf import settings
from django.core.exceptions import PermissionDenied
import functools


class NotAllowedInProductionException(Exception):
    pass


def not_in_production(func):
    """
    Decorator that raises exception if run in production.
    Typically used for management commands that changes production data.
    """

    def inner(*args, **kwargs):
        if settings.PRODUCTION or settings.ENVIRONMENT == "prod":
            raise NotAllowedInProductionException(
                "This operation is not allowed in production!"
            )

        return func(*args, **kwargs)

    return inner


def permission_required(permissions: str | list[str] | set[str], *, all_required=True):
    """
    Decorator that can be used alongside the any function to check if a user
    has a particular permission. Raises a PermissionDenied exception if user
    does not have the approariate permission.
    """

    if not isinstance(permissions, (list, set)):
        permissions = [permissions]

    def decorator(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            *_, info = args

            try:
                user = info.auth

                if not user:
                    raise PermissionDenied("User from context is unknown.")

                if not user.is_authenticated:
                    raise PermissionDenied("User is unauthenticated.")

                if all_required:
                    if not user.has_perms(permissions):
                        raise PermissionDenied(
                            "User does not have all the required permissions."
                        )
                else:
                    if not user.has_perm(permissions):
                        raise PermissionDenied(
                            "User does not have any of the required permissions."
                        )

                return func(*args, **kwargs)
            except AttributeError:
                raise AttributeError(
                    "Auth attribute on WSGIRequest does not exist. "
                    "Ensure that authentication for the endpointt is enabled "
                    "before using the permission_required decorator"
                )

        return inner

    return decorator
