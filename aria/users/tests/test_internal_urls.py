from django.urls import reverse


class TestInternalUsersUrls:
    def test_url_users_list(self):
        """
        Test reverse match of UserListAPI endpoint.
        """

        url = reverse("users-list")
        assert url == "/api/users/"

    def test_url_users_detail(self):
        """
        Test reverse match of UserDetailAPI endpoint.
        """

        url = reverse("users-detail", args=[1])
        assert url == "/api/users/1/"

    def test_url_users_update(self):
        """
        Test reverse match of UserUpdateAPI endpoint.
        """

        url = reverse("users-update", args=[1])
        assert url == "/api/users/1/update/"
