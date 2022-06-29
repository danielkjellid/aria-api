from typing import TYPE_CHECKING, Any

from django.contrib.auth.models import BaseUserManager

from aria.core.models import BaseQuerySet

if TYPE_CHECKING:
    from aria.users import models


class UserQuerySet(BaseQuerySet["models.User"]):
    """
    Custom user model manager where email is used as the unique identifier
    for authentication instead of usernames.
    """

    def create_user(
        self, email: str, password: str, **extra_fields: Any
    ) -> BaseQuerySet["models.User"]:
        """
        Create and save a user with the given email and password
        """

        if not email:
            raise ValueError("The email must be set")

        email = BaseUserManager.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()

        return user  # type: ignore

    def create_superuser(
        self, email: str, password: str, **extra_fields: Any
    ) -> BaseQuerySet["models.User"]:
        """
        Create and save a SuperUser with the given email and password
        """

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)
