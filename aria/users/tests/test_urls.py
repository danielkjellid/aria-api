from django.urls import reverse


class TestPublicUsersUrls:
    def test_url_user_create_api(self) -> None:
        """
        Test reverse match of user_create_api endpoint.
        """
        url = reverse("api-public-1.0.0:users-create")
        assert url == "/api/v1/users/create/"

    def test_url_user_account_verification_api(self) -> None:
        """
        Test reverse match of user_account_verification_api endpoint.
        """
        url = reverse("api-public-1.0.0:users-verify")
        assert url == "/api/v1/users/verify/"

    def test_url_user_account_verification_confirm_api(self) -> None:
        """
        Test reverse match of user_account_verification_confirm_api endpoint.
        """
        url = reverse("api-public-1.0.0:users-verify-confirm")
        assert url == "/api/v1/users/verify/confirm/"

    def test_url_user_password_reset_api(self) -> None:
        """
        Test reverse match of user_password_reset_api endpoint.
        """
        url = reverse("api-public-1.0.0:users-password-reset")
        assert url == "/api/v1/users/password/reset/"

    def test_url_user_password_reset_confirm_api(self) -> None:
        """
        Test reverse match of user_password_reset_confirm_api endpoint.
        """
        url = reverse("api-public-1.0.0:users-password-reset-confirm")
        assert url == "/api/v1/users/password/reset/confirm/"


class TestInternalUsersUrls:
    def test_url_user_list_api(self) -> None:
        """
        Test reverse match of user_list_api endpoint.
        """
        url = reverse("api-internal-1.0.0:users-index")
        assert url == "/api/v1/internal/users/"

    def test_url_user_detail_api(self) -> None:
        """
        Test reverse match of user_detail_api endpoint.
        """
        url = reverse("api-internal-1.0.0:users-user-{user_id}", args=["user_id"])
        assert url == "/api/v1/internal/users/user/user_id/"

    def test_url_user_update_api(self) -> None:
        """
        Test reverse match of user_update_api endpoint.
        """
        url = reverse(
            "api-internal-1.0.0:users-user-{user_id}-update", args=["user_id"]
        )
        assert url == "/api/v1/internal/users/user/user_id/update/"
