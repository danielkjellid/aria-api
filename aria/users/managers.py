from typing import TYPE_CHECKING

from django.contrib.auth.models import BaseUserManager

from aria.core.models import BaseQuerySet

if TYPE_CHECKING:
    pass


class UserQuerySet(BaseQuerySet["models.User"]):
    pass


class UserManager(BaseUserManager):
    """
    Default manager for the User model.
    """

    def create_user(self, *args, **kwargs):
        """Create a user"""
        raise RuntimeError("Please use the create_user service")

    def create_superuser(self, *args, **extra_fields):
        """Create a superuser"""
        raise RuntimeError("Please use the create_user service")
