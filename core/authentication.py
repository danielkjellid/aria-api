from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken


class JWTAuthenticationSafe(JWTAuthentication):
    def authenticate(self, request):
        try:
            return super().authenticate(request=request)
        except InvalidToken:
            return None