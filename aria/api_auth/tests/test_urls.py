from django.urls import reverse


class TestPublicAuthUrls:  # TODO: Remove /ninja/ when drf migration is done.
    def test_url_auth_obtain_token_pair(self) -> None:
        """
        Test reverse match of auth_obtain_token_pair_api endpoint.
        """
        url = reverse("api-public-1.0.0:auth-tokens-obtain")
        assert url == "/api/v1/auth/tokens/obtain/"

    def test_url_auth_refresh_token_pair(self) -> None:
        """
        Test reverse match of auth_refresh_token_pair_api endpoint.
        """
        url = reverse("api-public-1.0.0:auth-tokens-refresh")
        assert url == "/api/v1/auth/tokens/refresh/"

    def test_url_auth_log_out_and_blacklist_refresh_token(self) -> None:
        """
        Test reverse match of auth_log_out_and_blacklist_refresh_token_api endpoint.
        """
        url = reverse("api-public-1.0.0:auth-tokens-blacklist")
        assert url == "/api/v1/auth/tokens/blacklist/"
