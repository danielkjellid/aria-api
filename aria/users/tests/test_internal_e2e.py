from model_bakery import baker
import pytest
import json

from aria.test_utils import model_baker_datetime_formatting

from aria.users.models import User

pytestmark = pytest.mark.django_db


class TestInternalUsersEndpoints:

    base_endpoint = "/api/users/"

    #################
    # List endpoint #
    #################

    # Users list endpoint required both the permission has_users_list
    # and is_staff = True for the user.

    def test_unauthenticated_user_list(self, unauthenticated_client):
        """
        Test that unauthenticated users gets a 401 unauthorized on listing
        all users in the application.
        """

        response = unauthenticated_client.get(self.base_endpoint)

        assert response.status_code == 401

    def test_authenticated_unprivileged_user_list(
        self, authenticated_unprivileged_client
    ):
        """
        Test that authenticated, unprivileged, users gets a 403 forbidden on
        listing all users in the application.
        """

        response = authenticated_unprivileged_client.get(self.base_endpoint)

        assert response.status_code == 403

    @pytest.mark.parametrize("test_permissions", ["has_users_list"], indirect=True)
    def test_authenticated_privileged_user_list(self, authenticated_privileged_client):
        """
        Test that authenticated, privileged, users with staff = false gets 403
        forbidden on listing all users in the application.
        """

        response = authenticated_privileged_client.get(self.base_endpoint)

        assert response.status_code == 403

    @pytest.mark.parametrize("test_permissions", ["has_users_list"], indirect=True)
    def test_authenticated_privileged_staff_user_list(
        self, authenticated_privileged_staff_client
    ):
        """
        Test that privileged staff users gets a valid response on listing all users in
        the application.
        """
        baker.make(User, _quantity=3)

        response = authenticated_privileged_staff_client.get(self.base_endpoint)

        assert response.status_code == 200
        assert len(json.loads(response.content)) == 4  # The three made + fixture

    def test_authenticated_superuser_list(self, authenticated_superuser_client):
        """
        Test that superusers gets a valid response on listing all users in
        the application.
        """
        baker.make(User, _quantity=3)

        response = authenticated_superuser_client.get(self.base_endpoint)

        assert response.status_code == 200
        assert len(json.loads(response.content)) == 4  # The three made + fixture

    ###################
    # Detail endpoint #
    ###################

    # Users detail endpoint required both the permission has_users_list
    # and is_staff = True for the user.

    def test_unauthenticated_user_retrieve(self, unauthenticated_client):
        """
        Test that unauthenticated users gets a 401 unauthorized on another
        user retrieval.
        """

        user = baker.make(User)

        response = unauthenticated_client.get(f"{self.base_endpoint}{user.id}/")

        assert response.status_code == 401

    def test_authenticated_unprivileged_user_retrieve(
        self, authenticated_unprivileged_client
    ):
        """
        Test that authenticated, unprivileged, users gets a 403 forbidden on
        another user retrieval.
        """

        user = baker.make(User)

        response = authenticated_unprivileged_client.get(
            f"{self.base_endpoint}{user.id}/"
        )

        assert response.status_code == 403

    @pytest.mark.parametrize("test_permissions", ["has_users_list"], indirect=True)
    def test_authenticated_privileged_user_retrieve(
        self, authenticated_privileged_client
    ):
        """
        Test that authenticated, privileged, users with staff = false gets 403 forbidden
        on another user retrieval.
        """

        user = baker.make(User)

        response = authenticated_privileged_client.get(
            f"{self.base_endpoint}{user.id}/"
        )

        assert response.status_code == 403

    @pytest.mark.parametrize("test_permissions", ["has_users_list"], indirect=True)
    def test_authenticated_privileged_staff_user_retrieve(
        self, authenticated_privileged_staff_client
    ):
        """
        Test that privileged staff users gets a valid responseon another user
        retrieval.
        """
        user = baker.make(User)

        expected_json = {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "phone_number": user.formatted_phone_number,
            "birth_date": user.birth_date,
            "has_confirmed_email": user.has_confirmed_email,
            "last_login": user.last_login,
            "id": user.id,
            "profile": {
                "full_name": user.full_name,
                "initial": user.initial,
                "avatar_color": user.avatar_color,
            },
            # Datetimes are wonky, model bakery is one hour behind local tz
            "date_joined": model_baker_datetime_formatting(user.date_joined),
            "is_active": user.is_active,
            "full_address": user.full_address,
            "street_address": user.street_address,
            "zip_code": user.zip_code,
            "zip_place": user.zip_place,
            "acquisition_source": user.acquisition_source,
            "disabled_emails": user.disabled_emails,
            "subscribed_to_newsletter": user.subscribed_to_newsletter,
            "allow_personalization": user.allow_personalization,
            "allow_third_party_personalization": user.allow_personalization,
            "logs": [],
            "notes": [],
        }

        url = f"{self.base_endpoint}{user.id}/"

        response = authenticated_privileged_staff_client.get(url)
        actual_json = json.loads(response.content)

        assert response.status_code == 200
        assert actual_json == expected_json

    def test_authenticated_superuser_retrieve(self, authenticated_superuser_client):
        """
        Test that staff superusers users gets a valid response on another user
        retrieval.
        """
        user = baker.make(User)

        expected_json = {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "phone_number": user.formatted_phone_number,
            "birth_date": user.birth_date,
            "has_confirmed_email": user.has_confirmed_email,
            "last_login": user.last_login,
            "id": user.id,
            "profile": {
                "full_name": user.full_name,
                "initial": user.initial,
                "avatar_color": user.avatar_color,
            },
            # Datetimes are wonky, model bakery is one hour behind local tz
            "date_joined": model_baker_datetime_formatting(user.date_joined),
            "is_active": user.is_active,
            "full_address": user.full_address,
            "street_address": user.street_address,
            "zip_code": user.zip_code,
            "zip_place": user.zip_place,
            "acquisition_source": user.acquisition_source,
            "disabled_emails": user.disabled_emails,
            "subscribed_to_newsletter": user.subscribed_to_newsletter,
            "allow_personalization": user.allow_personalization,
            "allow_third_party_personalization": user.allow_personalization,
            "logs": [],
            "notes": [],
        }

        url = f"{self.base_endpoint}{user.id}/"

        response = authenticated_superuser_client.get(url)
        actual_json = json.loads(response.content)

        assert response.status_code == 200
        assert actual_json == expected_json

    ###################
    # Update endpoint #
    ###################

    # Users update endpoint required both the permission has_users_edit
    # and is_staff = True for the user.

    def test_unauthenticated_user_update(self, unauthenticated_client):
        """
        Test that unauthenticated users gets a 401 unauthorized on
        full update of another user instance.
        """

        user = baker.make(User)

        payload_json = {
            "email": "newtestuser@example,com",
            "first_name": "First",
            "last_name": "Last",
            "phone_number": "12345678",
            "has_confirmed_email": not user.has_confirmed_email,
            "zip_code": "1234",
            "zip_place": "Oslo",
            "disabled_emails": not user.disabled_emails,
            "subscribed_to_newsletter": not user.subscribed_to_newsletter,
            "allow_personalization": not user.allow_personalization,
            "allow_third_party_personalization": not user.allow_third_party_personalization,
        }

        response = unauthenticated_client.post(
            f"{self.base_endpoint}{user.id}/update/", data=payload_json, format="json"
        )

        assert response.status_code == 401

    def test_authenticated_unprivileged_user_update(
        self, authenticated_unprivileged_client
    ):
        """
        Test that authenticated, unprivileged, users gets a 403 forbidden
        on full update of another user instance.
        """

        user = baker.make(User)

        payload_json = {
            "email": "newtestuser@example,com",
            "first_name": "First",
            "last_name": "Last",
            "phone_number": "12345678",
            "has_confirmed_email": not user.has_confirmed_email,
            "zip_code": "1234",
            "zip_place": "Oslo",
            "disabled_emails": not user.disabled_emails,
            "subscribed_to_newsletter": not user.subscribed_to_newsletter,
            "allow_personalization": not user.allow_personalization,
            "allow_third_party_personalization": not user.allow_third_party_personalization,
        }

        response = authenticated_unprivileged_client.post(
            f"{self.base_endpoint}{user.id}/update/", data=payload_json, format="json"
        )

        assert response.status_code == 403

    @pytest.mark.parametrize("test_permissions", ["has_user_edit"], indirect=True)
    def test_authenticated_privileged_user_update(
        self, authenticated_privileged_client
    ):
        """
        Test that authenticated, privileged, users with staff = false
        gets 403 forbidden on full update of another user instance.
        """

        user = baker.make(User)

        payload_json = {
            "email": "newtestuser@example,com",
            "first_name": "First",
            "last_name": "Last",
            "phone_number": "12345678",
            "has_confirmed_email": not user.has_confirmed_email,
            "zip_code": "1234",
            "zip_place": "Oslo",
            "disabled_emails": not user.disabled_emails,
            "subscribed_to_newsletter": not user.subscribed_to_newsletter,
            "allow_personalization": not user.allow_personalization,
            "allow_third_party_personalization": not user.allow_third_party_personalization,
        }

        response = authenticated_privileged_client.post(
            f"{self.base_endpoint}{user.id}/update/", data=payload_json, format="json"
        )

        assert response.status_code == 403

    @pytest.mark.parametrize("test_permissions", ["has_user_edit"], indirect=True)
    def test_authenticated_privileged_staff_user_update(
        self, authenticated_privileged_staff_client
    ):
        """
        Test that privileged staff users gets a valid response on
        full update of another user instance.
        """

        user = baker.make(User)

        payload_json = {
            "email": "newtestuser@example.com",
            "first_name": "First",
            "last_name": "Last",
            "phone_number": "12345678",
            "has_confirmed_email": not user.has_confirmed_email,
            "zip_code": "1234",
            "zip_place": "Oslo",
            "disabled_emails": not user.disabled_emails,
            "subscribed_to_newsletter": not user.subscribed_to_newsletter,
            "allow_personalization": not user.allow_personalization,
            "allow_third_party_personalization": not user.allow_third_party_personalization,
        }

        response = authenticated_privileged_staff_client.post(
            f"{self.base_endpoint}{user.id}/update/", data=payload_json, format="json"
        )

        response_json = json.loads(response.content)

        assert response.status_code == 200
        assert response_json["data"] == payload_json

    def test_authenticated_superuser_update(self, authenticated_superuser_client):
        """
        Test that superusers gets a valid response on full update of
        another user instance.
        """

        user = baker.make(User)

        payload_json = {
            "email": "newtestuser@example.com",
            "first_name": "First",
            "last_name": "Last",
            "phone_number": "12345678",
            "has_confirmed_email": not user.has_confirmed_email,
            "zip_code": "1234",
            "zip_place": "Oslo",
            "disabled_emails": not user.disabled_emails,
            "subscribed_to_newsletter": not user.subscribed_to_newsletter,
            "allow_personalization": not user.allow_personalization,
            "allow_third_party_personalization": not user.allow_third_party_personalization,
        }

        response = authenticated_superuser_client.post(
            f"{self.base_endpoint}{user.id}/update/", data=payload_json, format="json"
        )

        response_json = json.loads(response.content)

        assert response.status_code == 200
        assert response_json["data"] == payload_json

    def test_unauthenticated_user_partial_update(self, unauthenticated_client):
        """
        Test that unauthenticated users gets a 401 unauthorized upon partial update.
        """

        user = baker.make(User)

        payload_json = {
            "email": "newtestuser@example,com",
        }

        response = unauthenticated_client.post(
            f"{self.base_endpoint}{user.id}/update/", data=payload_json, format="json"
        )

        assert response.status_code == 401

    def test_authenticated_unprivileged_user_partial_update(
        self, authenticated_unprivileged_client
    ):
        """
        Test that authenticated, unprivileged, users gets a 403 forbidden.
        """

        user = baker.make(User)

        payload_json = {
            "email": "newtestuser@example,com",
        }

        response = authenticated_unprivileged_client.post(
            f"{self.base_endpoint}{user.id}/update/", data=payload_json, format="json"
        )

        assert response.status_code == 403

    @pytest.mark.parametrize("test_permissions", ["has_user_edit"], indirect=True)
    def test_authenticated_privileged_user_partial_update(
        self, authenticated_privileged_client
    ):
        """
        Test that authenticated, privileged, users with staff = false gets 403 forbidden.
        """

        user = baker.make(User)

        payload_json = {
            "email": "newtestuser@example,com",
        }

        response = authenticated_privileged_client.post(
            f"{self.base_endpoint}{user.id}/update/", data=payload_json, format="json"
        )

        assert response.status_code == 403

    @pytest.mark.parametrize("test_permissions", ["has_user_edit"], indirect=True)
    def test_authenticated_privileged_staff_user_partial_update(
        self, authenticated_privileged_staff_client
    ):
        """
        Test that privileged staff users gets a valid response
        """

        user = baker.make(User)

        payload_json = {"email": "newtestuser@example.com"}

        response = authenticated_privileged_staff_client.post(
            f"{self.base_endpoint}{user.id}/update/", data=payload_json, format="json"
        )

        response_json = json.loads(response.content)

        assert response.status_code == 200
        assert response_json["data"] == payload_json

    def test_authenticated_superuser_partial_update(
        self, authenticated_superuser_client
    ):
        """
        Test that superusers gets a valid response
        """

        user = baker.make(User)

        payload_json = {"email": "newtestuser@example.com"}

        response = authenticated_superuser_client.post(
            f"{self.base_endpoint}{user.id}/update/", data=payload_json, format="json"
        )

        response_json = json.loads(response.content)

        assert response.status_code == 200
        assert response_json["data"] == payload_json
