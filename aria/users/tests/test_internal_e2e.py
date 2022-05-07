import json
from datetime import datetime

from django.contrib.sites.models import Site

import pytest
from model_bakery import baker

from aria.users.models import User

pytestmark = pytest.mark.django_db


class TestInternalUsersEndpoints:

    base_endpoint = "/api/users/"

    #################
    # List endpoint #
    #################

    # Users list endpoint required both the permission has_users_list
    # and is_staff = True for the user.

    def test_unauthenticated_user_list(
        self, unauthenticated_client, django_assert_max_num_queries
    ):
        """
        Test that unauthenticated users gets a 401 unauthorized on listing
        all users in the application.
        """

        with django_assert_max_num_queries(0):
            response = unauthenticated_client.get(self.base_endpoint)

        assert response.status_code == 401

    def test_authenticated_unprivileged_user_list(
        self, authenticated_unprivileged_client, django_assert_max_num_queries
    ):
        """
        Test that authenticated, unprivileged, users gets a 403 forbidden on
        listing all users in the application.
        """

        with django_assert_max_num_queries(1):
            response = authenticated_unprivileged_client.get(self.base_endpoint)

        assert response.status_code == 403

    @pytest.mark.parametrize("test_permissions", ["has_users_list"], indirect=True)
    def test_authenticated_privileged_user_list(
        self, authenticated_privileged_client, django_assert_max_num_queries
    ):
        """
        Test that authenticated, privileged, users with staff = false gets 403
        forbidden on listing all users in the application.
        """

        with django_assert_max_num_queries(1):
            response = authenticated_privileged_client.get(self.base_endpoint)

        assert response.status_code == 403

    @pytest.mark.parametrize("test_permissions", ["has_users_list"], indirect=True)
    def test_authenticated_privileged_staff_user_list(
        self, authenticated_privileged_staff_client, django_assert_max_num_queries
    ):
        """
        Test that privileged staff users gets a valid response on listing all users in
        the application.
        """
        baker.make(User, _quantity=3)

        with django_assert_max_num_queries(4):
            response = authenticated_privileged_staff_client.get(self.base_endpoint)

        assert response.status_code == 200
        assert len(json.loads(response.content)) == 4  # The three made + fixture

    def test_authenticated_superuser_list(
        self, authenticated_superuser_client, django_assert_max_num_queries
    ):
        """
        Test that superusers gets a valid response on listing all users in
        the application.
        """
        baker.make(User, _quantity=3)

        with django_assert_max_num_queries(4):
            response = authenticated_superuser_client.get(self.base_endpoint)

        assert response.status_code == 200
        assert len(json.loads(response.content)) == 4  # The three made + fixture

    ###################
    # Detail endpoint #
    ###################

    # Users detail endpoint required both the permission has_users_list
    # and is_staff = True for the user.

    def test_unauthenticated_user_retrieve(
        self, unauthenticated_client, django_assert_max_num_queries
    ):
        """
        Test that unauthenticated users gets a 401 unauthorized on another
        user retrieval.
        """

        user = baker.make(User)

        with django_assert_max_num_queries(0):
            response = unauthenticated_client.get(f"{self.base_endpoint}{user.id}/")

        assert response.status_code == 401

    def test_authenticated_unprivileged_user_retrieve(
        self, authenticated_unprivileged_client, django_assert_max_num_queries
    ):
        """
        Test that authenticated, unprivileged, users gets a 403 forbidden on
        another user retrieval.
        """

        user = baker.make(User)

        with django_assert_max_num_queries(1):
            response = authenticated_unprivileged_client.get(
                f"{self.base_endpoint}{user.id}/"
            )

        assert response.status_code == 403

    @pytest.mark.parametrize("test_permissions", ["has_users_list"], indirect=True)
    def test_authenticated_privileged_user_retrieve(
        self, authenticated_privileged_client, django_assert_max_num_queries
    ):
        """
        Test that authenticated, privileged, users with staff = false gets 403 forbidden
        on another user retrieval.
        """

        user = baker.make(User)

        with django_assert_max_num_queries(1):
            response = authenticated_privileged_client.get(
                f"{self.base_endpoint}{user.id}/"
            )

        assert response.status_code == 403

    @pytest.mark.parametrize("test_permissions", ["has_users_list"], indirect=True)
    def test_authenticated_privileged_staff_user_retrieve(
        self,
        authenticated_privileged_staff_client,
        django_assert_max_num_queries,
    ):
        """
        Test that privileged staff users gets a valid responseon another user
        retrieval.
        """
        user = baker.make(User)
        user.date_joined = datetime.fromisoformat("1970-01-01 21:00:00")
        user.save()

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
            "date_joined": "01. January 1970 21:00",
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

        with django_assert_max_num_queries(6):
            response = authenticated_privileged_staff_client.get(url)

        actual_json = json.loads(response.content)

        assert response.status_code == 200
        assert actual_json == expected_json

    def test_authenticated_superuser_retrieve(
        self, authenticated_superuser_client, django_assert_max_num_queries
    ):
        """
        Test that staff superusers users gets a valid response on another user
        retrieval.
        """

        user = baker.make(User)
        user.date_joined = datetime.fromisoformat("1970-01-01 21:00:00")
        user.save()

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
            "date_joined": "01. January 1970 21:00",
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

        with django_assert_max_num_queries(6):
            response = authenticated_superuser_client.get(url)

        actual_json = json.loads(response.content)

        assert response.status_code == 200
        assert actual_json == expected_json

    ###################
    # Update endpoint #
    ###################

    # Users update endpoint required both the permission has_users_edit
    # and is_staff = True for the user.

    def test_unauthenticated_user_update(
        self, unauthenticated_client, django_assert_max_num_queries
    ):
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

        with django_assert_max_num_queries(0):
            response = unauthenticated_client.post(
                f"{self.base_endpoint}{user.id}/update/",
                data=payload_json,
                format="json",
            )

        assert response.status_code == 401

    def test_authenticated_unprivileged_user_update(
        self, authenticated_unprivileged_client, django_assert_max_num_queries
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

        with django_assert_max_num_queries(1):
            response = authenticated_unprivileged_client.post(
                f"{self.base_endpoint}{user.id}/update/",
                data=payload_json,
                format="json",
            )

        assert response.status_code == 403

    @pytest.mark.parametrize("test_permissions", ["has_user_edit"], indirect=True)
    def test_authenticated_privileged_user_update(
        self, authenticated_privileged_client, django_assert_max_num_queries
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

        with django_assert_max_num_queries(1):
            response = authenticated_privileged_client.post(
                f"{self.base_endpoint}{user.id}/update/",
                data=payload_json,
                format="json",
            )

        assert response.status_code == 403

    @pytest.mark.parametrize("test_permissions", ["has_user_edit"], indirect=True)
    def test_authenticated_privileged_staff_user_update(
        self, authenticated_privileged_staff_client, django_assert_max_num_queries
    ):
        """
        Test that privileged staff users gets a valid response on
        full update of another user instance.
        """

        site = baker.make(Site)
        user = baker.make(User, **{"site": site})

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

        # The base query for getting users is 6 plus two for getting and checking
        # permissions, one for update and one additional for bulk creating log
        # entries. The last two is site lookup.
        with django_assert_max_num_queries(11):
            response = authenticated_privileged_staff_client.post(
                f"{self.base_endpoint}{user.id}/update/",
                data=payload_json,
                format="json",
            )

        response_json = json.loads(response.content)

        assert response.status_code == 200
        assert response_json["data"] == payload_json

    def test_authenticated_superuser_update(
        self, authenticated_superuser_client, django_assert_max_num_queries
    ):
        """
        Test that superusers gets a valid response on full update of
        another user instance.
        """

        site = baker.make(Site)
        user = baker.make(User, **{"site": site})

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

        # The base query for the users is 6 plus one additional for
        # bulk creating log entries + 2 queries for checking site.
        with django_assert_max_num_queries(9):
            response = authenticated_superuser_client.post(
                f"{self.base_endpoint}{user.id}/update/",
                data=payload_json,
                format="json",
            )

        response_json = json.loads(response.content)

        assert response.status_code == 200
        assert response_json["data"] == payload_json

    def test_unauthenticated_user_partial_update(
        self, unauthenticated_client, django_assert_max_num_queries
    ):
        """
        Test that unauthenticated users gets a 401 unauthorized upon partial update.
        """

        site = baker.make(Site)
        user = baker.make(User, **{"site": site})

        payload_json = {
            "email": "newtestuser@example,com",
        }

        with django_assert_max_num_queries(0):
            response = unauthenticated_client.post(
                f"{self.base_endpoint}{user.id}/update/",
                data=payload_json,
                format="json",
            )

        assert response.status_code == 401

    def test_authenticated_unprivileged_user_partial_update(
        self, authenticated_unprivileged_client, django_assert_max_num_queries
    ):
        """
        Test that authenticated, unprivileged, users gets a 403 forbidden.
        """

        user = baker.make(User)

        payload_json = {
            "email": "newtestuser@example,com",
        }

        with django_assert_max_num_queries(1):
            response = authenticated_unprivileged_client.post(
                f"{self.base_endpoint}{user.id}/update/",
                data=payload_json,
                format="json",
            )

        assert response.status_code == 403

    @pytest.mark.parametrize("test_permissions", ["has_user_edit"], indirect=True)
    def test_authenticated_privileged_user_partial_update(
        self, authenticated_privileged_client, django_assert_max_num_queries
    ):
        """
        Test that authenticated, privileged, users with staff = false gets 403 forbidden.
        """

        user = baker.make(User)

        payload_json = {
            "email": "newtestuser@example,com",
        }

        with django_assert_max_num_queries(1):
            response = authenticated_privileged_client.post(
                f"{self.base_endpoint}{user.id}/update/",
                data=payload_json,
                format="json",
            )

        assert response.status_code == 403

    @pytest.mark.parametrize("test_permissions", ["has_user_edit"], indirect=True)
    def test_authenticated_privileged_staff_user_partial_update(
        self, authenticated_privileged_staff_client, django_assert_max_num_queries
    ):
        """
        Test that privileged staff users gets a valid response
        """

        site = baker.make(Site)
        user = baker.make(User, **{"site": site})

        payload_json = {"email": "newtestuser@example.com"}

        # 6 queries for getting and updating the user, 2 queries for
        # getting and checking permissions and 1 query to log the change,
        # and 2 queries for checking site.
        with django_assert_max_num_queries(11):
            response = authenticated_privileged_staff_client.post(
                f"{self.base_endpoint}{user.id}/update/",
                data=payload_json,
                format="json",
            )

        response_json = json.loads(response.content)

        assert response.status_code == 200
        assert response_json["data"] == payload_json

    def test_authenticated_superuser_partial_update(
        self, authenticated_superuser_client, django_assert_max_num_queries
    ):
        """
        Test that superusers gets a valid response
        """

        site = baker.make(Site)
        user = baker.make(User, **{"site": site})

        payload_json = {"email": "newtestuser@example.com"}

        # 6 queries for getting and updating, 1 query to log the change
        # and 2 queries for checking site.
        with django_assert_max_num_queries(9):
            response = authenticated_superuser_client.post(
                f"{self.base_endpoint}{user.id}/update/",
                data=payload_json,
                format="json",
            )

            response_json = json.loads(response.content)

        assert response.status_code == 200
        assert response_json["data"] == payload_json
