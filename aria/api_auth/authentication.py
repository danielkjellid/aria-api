from typing import Any, Optional

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from ninja.security import HttpBearer

from aria.api_auth.selectors import access_token_is_valid
from aria.core.exceptions import ApplicationError
from aria.users.models import User


class JWTAuthRequired(HttpBearer):
    def authenticate(self, request: HttpRequest, token: str) -> User:
        try:
            # Decode provided token.
            is_token_valid, decoded_access_token = access_token_is_valid(token)

            # Obviously return false if access token is invalid.
            if not is_token_valid:
                return False

            if not decoded_access_token:
                return False

            # Sanity check that user_id in decoded token actually exist.
            try:
                user = User.objects.get(id=decoded_access_token.user_id)
            except User.DoesNotExist as exc:
                raise ObjectDoesNotExist(_("No user with provided id exist.")) from exc

            # Also check that the user is active before returning a valid
            # response.
            if not user.is_active:
                raise ApplicationError(
                    "User with provided id is inactive", status_code=401
                )

            # If all checks passes, return endpoint.
            return user  # 200 OK
        # Any exception we want it to return False i.e. 401
        except Exception:  # pylint: disable=broad-except
            return False


class JWTAuthStaffRequired(JWTAuthRequired):
    def authenticate(self, request: HttpRequest, token: str) -> Optional[Any]:
        try:
            user = super().authenticate(request=request, token=token)

            if not user.is_staff:
                raise ApplicationError(
                    "User with provided id is not staff", status_code=401
                )

            return user

        except Exception:  # pylint: disable=broad-except
            return False
