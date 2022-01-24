from model_bakery import baker
import pytest
import json

from aria.users.models import User

pytestmark = pytest.mark.django_db


class TestPublicUsersEndpoints:

    base_endpoint = "/api/users"

    ###################
    # Create endpoint #
    ###################

    # Users create endpoint is publically available.

    create_endpoint = f"{base_endpoint}/create/"

    def test_unauthenticated_user_create(self, unauthenticated_client):
        user = baker.prepare(User)

        expected_json = {
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

        response = unauthenticated_client.post(
            self.create_endpoint, data=expected_json, format="json"
        )

        # Password won't be returned if the created object, so remove it
        expected_json.pop("password")

        assert response.status_code == 201
        assert json.loads(response.content) == expected_json

    ###################
    # Create endpoint #
    ###################
