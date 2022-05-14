from django.urls import reverse


class TestPublicAuthUrls:  # TODO: Remove /ninja/ when drf migration is done.
    def test_url_auth_obtain_token_pair(self):
        """
        Test reverse match of auth_obtain_token_pair endpoint.
        """
        url = reverse("api-1.0.0:auth-tokens-obtain")
        assert url == "/api/ninja/auth/tokens/obtain/"

    def test_url_auth_refresh_token_pair(self):
        """
        Test reverse match of auth_refresh_token_pair endpoint.
        """
        url = reverse("api-1.0.0:auth-tokens-refresh")
        assert url == "/api/ninja/auth/tokens/refresh/"

    def test_url_auth_log_out_and_blacklist_refresh_token(self):
        """
        Test reverse match of auth_log_out_and_blacklist_refresh_token endpoint.
        """
        url = reverse("api-1.0.0:auth-tokens-blacklist")
        assert url == "/api/ninja/auth/tokens/blacklist/"
