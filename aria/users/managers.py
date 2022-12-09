from typing import TYPE_CHECKING, Any

from django.contrib.auth.models import BaseUserManager
from django.contrib.postgres.aggregates import ArrayAgg

from aria.core.managers import BaseQuerySet

if TYPE_CHECKING:
    from aria.users import models  # noqa


class UserQuerySet(BaseQuerySet["models.User"]):
    def annotate_permissions(self) -> BaseQuerySet["models.User"]:
        """
        Annotate lists of user and group permissions.
        """

        return self.annotate(
            user_perms=ArrayAgg("user_permissions__codename", default=[]),
            group_perms=ArrayAgg("groups__permissions__codename", default=[]),
        )


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
