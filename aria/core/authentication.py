from typing import Any, Optional

from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from django.contrib.sites.models import Site
from django.http import HttpRequest

from aria.users.models import User


class AuthBackend(ModelBackend):
    """
    Custom authentication backend to support login for multiple sites
    """

    def authenticate(
        self,
        request: Optional[HttpRequest],
        username: Optional[str] = None,
        password: Optional[str] = None,
        **kwargs: Any,
    ) -> User | None:
        try:
            user = User.objects.get(email=username)
            # check if user is not associated with site that
            # the login request originates from
            if user.site != Site.objects.get(pk=settings.SITE_ID):
                return None

            if user and password and user.check_password(password):
                return user
            return None
        except User.DoesNotExist:
            return None

    def get_user(self, user_id: int) -> User | None:
        try:
            return User.objects.get(
                id=user_id, site=Site.objects.get(pk=settings.SITE_ID)
            )
        except User.DoesNotExist:
            return None
