import json

from django.contrib.auth.tokens import default_token_generator

import pytest
from model_bakery import baker

from aria.users.models import User

pytestmark = pytest.mark.django_db


class TestPublicUsersEndpoints:

    base_endpoint = "/api/users"

    ###################
    # Create endpoint #
    ###################

    # Users create endpoint is publically available.

    create_endpoint = f"{base_endpoint}/create/"

    def test_unauthenticated_user_create(
        self, unauthenticated_client, django_assert_max_num_queries
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
            "has_confirmed_email": user.has_confirmed_email,
            "street_address": user.street_address,
            "zip_code": user.zip_code,
            "zip_place": user.zip_place,
            "disabled_emails": user.disabled_emails,
            "subscribed_to_newsletter": user.subscribed_to_newsletter,
            "allow_personalization": user.allow_personalization,
            "allow_third_party_personalization": user.allow_third_party_personalization,
            "password": user.password,
        }

        # 1 query for checking if the user already exists, and one for
        # creating the new user.
        with django_assert_max_num_queries(2):
            response = unauthenticated_client.post(
                self.create_endpoint, data=payload_json, format="json"
            )

        response_json = json.loads(response.content)

        # Password won't be returned if the created object, so remove it
        payload_json.pop("password")

        assert response.status_code == 201
        assert response_json["data"] == payload_json

    ######################################
    # User account verification endpoint #
    ######################################

    verification_endpoint = f"{base_endpoint}/verify/"

    def test_unauthenticated_user_verify_account(
        self, unauthenticated_client, django_assert_max_num_queries
    ):
        """
        Test initiating the account verification process.
        """

        user = baker.make(User)

        payload_json = {"email": user.email}

        with django_assert_max_num_queries(1):
            response = unauthenticated_client.post(
                f"{self.verification_endpoint}", data=payload_json, format="json"
            )

        assert response.status_code == 200

    ######################################
    # User account verification endpoint #
    ######################################

    def test_unauthenticated_user_verify_account_confirm(
        self, unauthenticated_client, django_assert_max_num_queries
    ):
        """
        Test actually verifying the account
        """

        user = baker.make(User)
        user_uid = user.uid
        user_token = user.generate_verification_email_token()

        payload_json = {"uid": user_uid, "token": user_token}

        url = f"{self.verification_endpoint}confirm/{user_uid}/{user_token}/"

        # 1 for getting the user and 1 for updating the email
        with django_assert_max_num_queries(2):
            response = unauthenticated_client.post(
                url, data=payload_json, format="json"
            )

        assert response.status_code == 200

    ######################
    # User rest password #
    ######################

    reset_password_endpoint = f"{base_endpoint}/password/reset/"

    def test_unauthenticated_user_set_new_password(
        self, unauthenticated_client, django_assert_max_num_queries
    ):
        """
        Test initiating reset password process.
        """

        user = baker.make(User)

        payload_json = {"email": user.email}

        with django_assert_max_num_queries(2):
            response = unauthenticated_client.post(
                self.reset_password_endpoint, data=payload_json, format="json"
            )

        assert response.status_code == 200

    ##################################
    # User set rest password confirm #
    ##################################

    def test_unauthenticated_user_set_new_password_confirm(
        self, unauthenticated_client, django_assert_max_num_queries
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

        url = f"{self.reset_password_endpoint}confirm/{user_uid}/{user_token}/"

        with django_assert_max_num_queries(2):
            response = unauthenticated_client.post(
                url, data=payload_json, format="json"
            )

        assert response.status_code == 200
