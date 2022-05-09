import json

from django.contrib.auth.tokens import default_token_generator

import pytest
from model_bakery import baker

from aria.users.models import User

pytestmark = pytest.mark.django_db


class TestPublicUsersEndpoints:

    base_endpoint = "/api/users"

    verification_endpoint = f"{base_endpoint}/verify/"

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

        # 1 query for getting, 1 for updating and 1 for getting site.
        with django_assert_max_num_queries(3):
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
