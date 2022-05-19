from django.urls import reverse


class TestPublicUsersUrls:
    def test_url_user_create_api(self):
        """
        Test reverse match of user_create_api endpoint.
        """
        url = reverse("api-1.0.0:users-create")
        assert url == "/api/users/create/"

    def test_url_user_account_verification_api(self):
        """
        Test reverse match of user_account_verification_api endpoint.
        """
        url = reverse("api-1.0.0:users-verify")
        assert url == "/api/users/verify/"

    def test_url_user_account_verification_confirm_api(self):
        """
        Test reverse match of user_account_verification_confirm_api endpoint.
        """
        url = reverse("api-1.0.0:users-verify-confirm")
        assert url == "/api/users/verify/confirm/"

    def test_url_user_password_reset_api(self):
        """
        Test reverse match of user_password_reset_api endpoint.
        """
        url = reverse("api-1.0.0:users-password-reset")
        assert url == "/api/users/password/reset/"

    def test_url_user_password_reset_confirm_api(self):
        """
        Test reverse match of user_password_reset_confirm_api endpoint.
        """
        url = reverse("api-1.0.0:users-password-reset-confirm")
        assert url == "/api/users/password/reset/confirm/"


class TestPrivateUsersUrls:
    def test_url_user_list_api(self):
        """
        Test reverse match of user_list_api endpoint.
        """
        url = reverse("api-1.0.0:users-index")
        assert url == "/api/users/"

    def test_url_user_detail_api(self):
        """
        Test reverse match of user_detail_api endpoint.
        """
        url = reverse("api-1.0.0:users-{user_id}", args=["user_id"])
        assert url == "/api/users/user_id/"

    def test_url_user_update_api(self):
        url = reverse("api-1.0.0:users-{user_id}-update", args=["user_id"])
        assert url == "/api/users/user_id/update/"
