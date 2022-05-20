import json
from django.contrib.sites.models import Site
from django.contrib.auth.tokens import default_token_generator
from datetime import datetime
import pytest
from model_bakery import baker

from aria.users.models import User

pytestmark = pytest.mark.django_db


class TestPublicUsersEndpoints:

    BASE_ENDPOINT = "/api/users"

    def test_anonymous_request_user_create(
        self, anonymous_client, django_assert_max_num_queries, mocker
    ):
        """
        Test creating a user from the endpoint.
        """

        user = baker.prepare(User)

        payload_json = {
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "phone_number": user.phone_number,
            "street_address": user.street_address,
            "zip_code": user.zip_code,
            "zip_place": user.zip_place,
            "subscribed_to_newsletter": user.subscribed_to_newsletter,
            "allow_personalization": user.allow_personalization,
            "allow_third_party_personalization": user.allow_third_party_personalization,
            "password": user.password,
        }

        service_mock = mocker.patch("aria.users.endpoints.public.user_create")

        # 1 query for checking if the user already exists, and one for
        # creating the new user.
        with django_assert_max_num_queries(2):
            response = anonymous_client.post(
                f"{self.BASE_ENDPOINT}/create/",
                data=payload_json,
                content_type="application/json",
            )

        assert response.status_code == 201
        assert service_mock.call_count == 1
        # Endpoint consumes kwargs of request, so it should match
        # what's being called in the service.
        assert service_mock.call_args_list[0].kwargs == payload_json

    def test_anonymous_request_user_verify_account(
        self, anonymous_client, django_assert_max_num_queries
    ):
        """
        Test initiating the account verification process.
        """

        # Create a user to test that we are able to find
        # a user, and send a confirmation email.
        user = baker.make(User)

        payload_json = {"email": user.email}

        with django_assert_max_num_queries(1):
            response = anonymous_client.post(
                f"{self.BASE_ENDPOINT}/verify/",
                data=payload_json,
                content_type="application/json",
            )

        # Assert that we return a valid response.
        assert response.status_code == 200

        # Test that the logic in returns appropriate status
        # code if user with email is not found.
        with django_assert_max_num_queries(1):
            failed_response = anonymous_client.post(
                f"{self.BASE_ENDPOINT}/verify/",
                data={"email": "doesnotexist@example.com"},
                content_type="application/json",
            )

        # Assert that appropraite response is returned.
        assert failed_response.status_code == 404

    def test_anonymous_request_user_verify_account_confirm(
        self, anonymous_client, django_assert_max_num_queries, mocker
    ):
        """
        Test actually verifying the account
        """

        user = baker.make(User)
        user_uid = user.uid
        user_token = user.generate_verification_email_token()

        payload_json = {"uid": user_uid, "token": user_token}

        service_mock = mocker.patch("aria.users.endpoints.public.user_verify_account")

        # 1 for getting the user and 1 for updating the email
        with django_assert_max_num_queries(2):
            response = anonymous_client.post(
                f"{self.BASE_ENDPOINT}/verify/confirm/",
                data=payload_json,
                content_type="application/json",
            )

        assert response.status_code == 200
        assert service_mock.call_count == 1
        # Endpoint consumes kwargs of request, so it should match
        # what's being called in the service.
        assert service_mock.call_args_list[0].kwargs == {
            "uid": user_uid,
            "token": user_token,
        }

    def test_anonymous_request_user_password_reset(
        self, anonymous_client, django_assert_max_num_queries
    ):
        """
        Test initiating reset password process.
        """

        user = baker.make(User)

        payload_json = {"email": user.email}

        # 1 query for getting, 1 for updating and 1 for getting site.
        with django_assert_max_num_queries(3):
            response = anonymous_client.post(
                f"{self.BASE_ENDPOINT}/password/reset/",
                data=payload_json,
                content_type="application/json",
            )

        assert response.status_code == 200

        # Test that the logic in returns appropriate status
        # code if user with email is not found.
        with django_assert_max_num_queries(1):
            failed_response = anonymous_client.post(
                f"{self.BASE_ENDPOINT}/password/reset/",
                data={"email": "doesnotexist@example.com"},
                content_type="application/json",
            )

        # Assert that appropraite response is returned.
        assert failed_response.status_code == 404

    def test_anonymous_request_user_password_reset_confirm(
        self, anonymous_client, django_assert_max_num_queries, mocker
    ):
        """
        Test validating created tokens and setting new password.
        """

        user = baker.make(User)
        user_uid = user.uid
        user_token = default_token_generator.make_token(user)

        payload_json = {
            "new_password": "supersecret",
            "uid": user_uid,
            "token": user_token,
        }

        service_mock = mocker.patch("aria.users.endpoints.public.user_set_password")

        with django_assert_max_num_queries(2):
            response = anonymous_client.post(
                f"{self.BASE_ENDPOINT}/password/reset/confirm/",
                data=payload_json,
                content_type="application/json",
            )

        assert response.status_code == 200
        assert service_mock.call_count == 1
        assert service_mock.call_args_list[0].kwargs == {
            "uid": user_uid,
            "token": user_token,
            "new_password": "supersecret",
        }


class TestProtectedUsersEndpoints:

    BASE_ENDPOINT = "/api/users"

    #################
    # List endpoint #
    #################

    # The users list endpoint requires authorization and the permission
    # has_users_list for the user or user group.

    def test_anonymous_client_users_list(
        self, anonymous_client, django_assert_max_num_queries
    ):
        """
        Test that unauthenticated users gets a 401 unauthorized on listing
        all users in the application.
        """

        with django_assert_max_num_queries(0):
            response = anonymous_client.get(
                f"{self.BASE_ENDPOINT}/",
                content_type="application/json",
            )

        assert response.status_code == 401

    def test_authenticated_unprivileged_client_users_list(
        self,
        n_authenticated_unprivileged_client,
        django_assert_max_num_queries,
    ):
        """
        Test that authenticated, unprivileged, users gets a 403 forbidden on
        listing all users in the application.
        """

        # Uses 3 quieries: 1 for getting the user, 2 for checking permissions.
        with django_assert_max_num_queries(3):
            response = n_authenticated_unprivileged_client.get(
                f"{self.BASE_ENDPOINT}/",
                content_type="application/json",
            )

        assert response.status_code == 403

    @pytest.mark.parametrize("test_permissions", ["has_users_list"], indirect=True)
    def test_authenticated_privileged_client_users_list(
        self, n_authenticated_privileged_client, django_assert_max_num_queries
    ):
        """
        Test that privileged users gets a valid response on listing all users in
        the application.
        """

        baker.make("users.User", _quantity=3)

        # Uses 5 queries: 1 for getting request user, 2 for checking permissions,
        # 2 for getting users and pagination data.
        with django_assert_max_num_queries(5):
            response = n_authenticated_privileged_client.get(
                f"{self.BASE_ENDPOINT}/",
                content_type="application/json",
            )

        assert response.status_code == 200
        assert (
            len(json.loads(response.content)["data"]) == 4
        )  # The three made + fixture

    ###################
    # Detail endpoint #
    ###################

    # The user detail endpoint requires authorization and the permission
    # has_users_list for the user or user group.

    def test_anonymous_client_user_detail(
        self, anonymous_client, django_assert_max_num_queries
    ):
        """
        Test that unauthenticated users gets a 401 unauthorized on
        user retrieval.
        """

        user = baker.make("users.User")

        with django_assert_max_num_queries(0):
            response = anonymous_client.get(
                f"{self.BASE_ENDPOINT}/{user.id}/",
                content_type="application/json",
            )

        assert response.status_code == 401

    def test_authenticated_unprivileged_client_user_detail(
        self,
        n_authenticated_unprivileged_client,
        django_assert_max_num_queries,
    ):
        """
        Test that authenticated, unprivileged, users gets a 403 forbidden on
        user retrieval.
        """

        user = baker.make("users.User")

        # Uses 3 queries: 1 for getting the user, 2 for checking permissions.
        with django_assert_max_num_queries(3):
            response = n_authenticated_unprivileged_client.get(
                f"{self.BASE_ENDPOINT}/{user.id}/",
                content_type="application/json",
            )

        assert response.status_code == 403

    @pytest.mark.parametrize("test_permissions", ["has_users_list"], indirect=True)
    def test_authenticated_privileged_client_user_detail(
        self,
        n_authenticated_privileged_client,
        django_assert_max_num_queries,
    ):
        """
        Test that authenticated privileged users gets a valid response on retriving a
        single user instance.
        """

        user = baker.make("users.User")
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
            "date_joined": "1970-01-01T20:00:00Z",
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

        # Uses 6 queries: 1 for getting request user, 2 for getting and checking permissions,
        # 1 for getting notes associated with user, and 1 for getting audit logs.
        with django_assert_max_num_queries(6):
            response = n_authenticated_privileged_client.get(
                f"{self.BASE_ENDPOINT}/{user.id}/",
                content_type="application/json",
            )

        actual_json = json.loads(response.content)

        assert response.status_code == 200
        assert actual_json == expected_json

    ###################
    # Update endpoint #
    ###################

    # The user update endpoint requires authorization and the permission
    # has_user_edot for the user or user group.

    def test_anonymous_client_user_update(
        self, anonymous_client, django_assert_max_num_queries
    ):
        """
        Test that unauthenticated users gets a 401 unauthorized on
        full update of another user instance.
        """

        user = baker.make("users.User")

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
            response = anonymous_client.post(
                f"{self.BASE_ENDPOINT}/{user.id}/update/",
                data=payload_json,
                content_type="application/json",
            )

        assert response.status_code == 401

    def test_authenticated_unprivileged_client_user_update(
        self, n_authenticated_unprivileged_client, django_assert_max_num_queries
    ):
        """
        Test that authenticated, unprivileged, users gets a 403 forbidden
        on full update of another user instance.
        """

        user = baker.make("users.User")

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

        # Uses 3 queries: 1 for getting the user, 2 for checking permissions.
        with django_assert_max_num_queries(3):
            response = n_authenticated_unprivileged_client.post(
                f"{self.BASE_ENDPOINT}/{user.id}/update/",
                data=payload_json,
                content_type="application/json",
            )

        assert response.status_code == 403

    @pytest.mark.parametrize("test_permissions", ["has_user_edit"], indirect=True)
    def test_authenticated_privileged_client_user_update(
        self, n_authenticated_privileged_client, django_assert_max_num_queries
    ):
        """
        Test that privileged users gets a valid response on
        full update of another user instance.
        """

        site = baker.make(Site)
        user = baker.make("users.User", **{"site": site})

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

        # Uses 11 queries: 1 for getting user, 2 for checking permissions,
        # 1 for getting user to update, 1 savepoint for atomic transaction,
        # 1 for getting site, 2 for getting user + site, 1 for updating user,
        # 1 for bulk creating log entries, 1 for getting site, and 1 for
        # releasing savepoint.
        with django_assert_max_num_queries(12):
            response = n_authenticated_privileged_client.post(
                f"{self.BASE_ENDPOINT}/{user.id}/update/",
                data=payload_json,
                content_type="application/json",
            )

        user.refresh_from_db()

        assert response.status_code == 200
        assert user.email == "newtestuser@example.com"
        assert user.first_name == "First"
        assert user.last_name == "Last"
        assert user.phone_number == "12345678"
        assert user.zip_code == "1234"
        assert user.zip_place == "Oslo"

    def test_anonymous_client_user_partial_update(
        self, anonymous_client, django_assert_max_num_queries
    ):
        """
        Test that unauthenticated users gets a 401 unauthorized upon partial update.
        """

        user = baker.make("users.User")

        payload_json = {"email": "somenewemail@example.com"}

        with django_assert_max_num_queries(0):
            response = anonymous_client.post(
                f"{self.BASE_ENDPOINT}/{user.id}/update/",
                data=payload_json,
                content_type="application/json",
            )

        assert response.status_code == 401

    def test_authenticated_unprivileged_client_user_partial_update(
        self, n_authenticated_unprivileged_client, django_assert_max_num_queries
    ):
        """
        Test that authenticated, unprivileged, users gets a 403 forbidden
        on partial update of another user instance.
        """

        user = baker.make("users.User")

        payload_json = {"email": "somenewemail@example.com"}

        # Uses 3 queries: 1 for getting the user, 2 for checking permissions.
        with django_assert_max_num_queries(3):
            response = n_authenticated_unprivileged_client.post(
                f"{self.BASE_ENDPOINT}/{user.id}/update/",
                data=payload_json,
                content_type="application/json",
            )

        assert response.status_code == 403

    @pytest.mark.parametrize("test_permissions", ["has_user_edit"], indirect=True)
    def test_authenticated_privileged_client_user_partial_update(
        self, n_authenticated_privileged_client, django_assert_max_num_queries
    ):
        """
        Test that privileged users gets a valid response on
        partial update of another user instance.
        """

        site = baker.make(Site)
        user = baker.make("users.User", **{"site": site})

        payload_json = {"email": "newtestuser@example.com"}

        # Uses 11 queries: 1 for getting user, 2 for checking permissions,
        # 1 for getting user to update, 1 savepoint for atomic transaction,
        # 1 for getting site, 2 for getting user + site, 1 for updating user,
        # 1 for bulk creating log entries 1 for getting site, and 1 for
        # releasing savepoint.
        with django_assert_max_num_queries(12):
            response = n_authenticated_privileged_client.post(
                f"{self.BASE_ENDPOINT}/{user.id}/update/",
                data=payload_json,
                content_type="application/json",
            )

        user.refresh_from_db()

        assert response.status_code == 200
        assert user.email == "newtestuser@example.com"
