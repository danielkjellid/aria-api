import jwt
from ninja.security import HttpBearer
from django.http import HttpRequest
from typing import Optional, Any
from django.conf import settings


class JWTAuthBearer(HttpBearer):
    def authenticate(self, request: HttpRequest, token: str) -> Optional[Any]:
        try:
            payload = jwt.decode(
                token, settings.JWT_SIGNING_KEY, algorithms=[settings.JWT_ALGORITHM]
            )
            user_id = payload.get("user_id", None)

            if user_id is None:
                return None
        except jwt.PyJWTError as exc:
            return None

        return user_id
