from django.urls import reverse


class TestPublicAuthUrls:
    def test_url_auth_tokens_obtain(self):
        """
        Test reverse match of AuthTokenObtainAPI endpoint.
        """

        url = reverse("auth-tokens-obtain")
        assert url == "/api/auth/tokens/obtain/"

    def test_url_auth_tokens_refresh(self):
        """
        Test reverse match of TokenRefreshView endpoint.
        """

        url = reverse("auth-tokens-refresh")
        assert url == "/api/auth/tokens/refresh/"

    def test_url_auth_tokens_blacklist(self):
        """
        Test reverse match of AuthLogoutAndBlacklistRefreshTokenForUserAPI
        endpoint.
        """

        url = reverse("auth-tokens-blacklist")
        assert url == "/api/auth/tokens/blacklist/"
