from typing import Any, Optional

from django.http import HttpRequest

from ninja.security import HttpBearer

from aria.api_auth.selectors import access_token_is_valid
from aria.core.exceptions import ApplicationError
from aria.users.models import User


class JWTAuthRequired(HttpBearer):
    def authenticate(self, request: HttpRequest, token: str) -> Optional[Any]:
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
            except User.DoesNotExist:
                raise ApplicationError(
                    "No user with provided id exist", status_code=404
                )

            # Also check that the user is active before returning a valid
            # response.
            if not user.is_active:
                raise ApplicationError(
                    "User with provided id is inactive", status_code=403
                )

            # If all checks passes, return endpoint.
            return user  # 200 OK
        # Any exception we want it to return False i.e 401
        except Exception:
            return False
