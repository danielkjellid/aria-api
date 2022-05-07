from django.urls import reverse


class TestPublicUsersUrls:
    def test_url_users_create(self):
        """
        Test reverse match of UserCreateAPI endpoint.
        """

        url = reverse("users-create")
        assert url == "/api/users/create/"

    def test_url_users_verify(self):
        """
        Test reverse match of UserAccountVerificationAPI endpoint.
        """

        url = reverse("users-verify")
        assert url == "/api/users/verify/"

    def test_url_users_verify_confirm(self):
        """
        Test reverse match of UserAccountVerificationConfirmAPI endpoint.
        """

        url = reverse("users-verify-confirm", args=["some_uid", "some_token"])
        assert url == "/api/users/verify/confirm/some_uid/some_token/"

    def test_url_users_password_reset(self):
        """
        Test reverse match of UserPasswordResetAPI endpoint.
        """

        url = reverse("users-reset-password")
        assert url == "/api/users/password/reset/"

    def test_url_users_password_confirm(self):
        """
        Test reverse match of UserAccountVerificationConfirmAPI endpoint.
        """

        url = reverse("users-reset-password-confirm", args=["some_uid", "some_token"])
        assert url == "/api/users/password/reset/confirm/some_uid/some_token/"
