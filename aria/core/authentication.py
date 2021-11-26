from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.contrib.sites.models import Site

User = get_user_model()


class AuthBackend(ModelBackend):
    """
    Custom authentication backend to support login for multiple sites
    """

    def authenticate(self, request, username=None, password=None):
        try:
            user = User.objects.get(email=username)
            # check if user is not associated with site that
            # the login request originates from
            if user.site != Site.objects.get(pk=settings.SITE_ID):
                return None
            else:
                if user.check_password(password):
                    return user
                return None
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(
                id=user_id, site=Site.objects.get(pk=settings.SITE_ID)
            )
        except User.DoesNotExist:
            return None
