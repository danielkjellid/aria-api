import json

import pytest
from model_bakery import baker
from aria.users.models import User
from django.contrib.auth.tokens import default_token_generator

from aria.core.exceptions import ApplicationError
from pydantic.error_wrappers import ValidationError as PydanticValidationError
from django.core.exceptions import ValidationError as DjangoValidationError

pytestmark = pytest.mark.django_db


class TestPublicUsersEndpoints:

    BASE_ENDPOINT = "/test/users"

    def test_anonymous_request_user_create(
        self, anonymous_client, django_assert_max_num_queries, mocker
    ):
        """
        Test creating a user from the endpoint.
        """

        # Test that bad data failes (returns a 400).
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

        service_mock = mocker.patch("aria.users.viewsets.public.user_create")

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

        service_mock = mocker.patch("aria.users.viewsets.public.user_create")

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

        service_mock = mocker.patch("aria.users.viewsets.public.user_set_password")

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
    pass
