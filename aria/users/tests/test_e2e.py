from model_bakery import baker
import pytest
import json

from aria.users.models import User

pytestmark = pytest.mark.django_db


class TestInternalUsersEndpoints:

    base_endpoint = "/api/users"

    #################
    # List endpoint #
    #################

    # Users list endpoint required both the permission has_users_list
    # and is_staff = True for the user.

    list_endpoint = f"{base_endpoint}/"

    def test_unauthenticated_user_list(self, unauthenticated_client):
        """
        Test that unauthenticated users gets a 401 unauthorized.
        """

        response = unauthenticated_client.get(self.list_endpoint)

        assert response.status_code == 401

    def test_authenticated_unprivileged_user_list(
        self, authenticated_unprivileged_client
    ):
        """
        Test that authenticated, unprivileged, users gets a 403 forbidden.
        """

        response = authenticated_unprivileged_client.get(self.list_endpoint)

        assert response.status_code == 403

    @pytest.mark.parametrize("test_permissions", ["has_users_list"], indirect=True)
    def test_authenticated_privileged_user_list(self, authenticated_privileged_client):
        """
        Test that authenticated, privileged, users with staff = false gets 403 forbidden.
        """

        response = authenticated_privileged_client.get(self.list_endpoint)

        assert response.status_code == 403

    @pytest.mark.parametrize("test_permissions", ["has_users_list"], indirect=True)
    def test_authenticated_privileged_staff_user_list(
        self, authenticated_privileged_staff_client
    ):
        """
        Test that privileged staff users gets a valid response
        """
        baker.make(User, _quantity=3)

        response = authenticated_privileged_staff_client.get(self.list_endpoint)

        assert response.status_code == 200
        assert len(json.loads(response.content)) == 4  # The three made + fixture

    def test_authenticated_superuser_list(self, authenticated_superuser_client):
        baker.make(User, _quantity=3)

        response = authenticated_superuser_client.get(self.list_endpoint)

        assert response.status_code == 200
        assert len(json.loads(response.content)) == 4  # The three made + fixture

    ###################
    # Create endpoint #
    ###################
