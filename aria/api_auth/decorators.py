import functools
from typing import Any, Callable, TypeVar

from django.core.exceptions import PermissionDenied

F = TypeVar("F", bound=Callable[..., Any])


def permission_required(
    permissions: str | list[str] | set[str], *, all_required: bool = True
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Decorator that can be used alongside the any function to check if a user
    has a particular permission. Raises a PermissionDenied exception if user
    does not have the appropriate permission.
    """

    if not isinstance(permissions, (list, set)):
        permissions = [permissions]

    def decorator(func: Any) -> Callable[..., Any]:
        @functools.wraps(func)
        def inner(*args: Any, **kwargs: Any) -> Any:
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
            except AttributeError as exc:
                raise AttributeError(
                    "Auth attribute on WSGIRequest does not exist. "
                    "Ensure that authentication for the endpoint is enabled "
                    "before using the permission_required decorator"
                ) from exc

        return inner

    return decorator
