from typing import TYPE_CHECKING, Any

from django.contrib.auth.models import BaseUserManager

from aria.core.models import BaseQuerySet

if TYPE_CHECKING:
    from aria.users import models  # noqa


class UserQuerySet(BaseQuerySet["models.User"]):
    pass


class UserManager(BaseUserManager["models.User"]):
    """
    Default manager for the User model.
    """

    def create_user(self, *args: Any, **kwargs: Any) -> None:
        """Create a user"""
        raise RuntimeError("Please use the create_user service")

    def create_superuser(self, *args: Any, **kwargs: Any) -> None:
        """Create a superuser"""
        raise RuntimeError("Please use the create_user service")
