import pytest
from model_bakery import baker

from aria.users.models import User
from aria.users.viewsets.public import (
    UserAccountVerificationAPI,
    UserAccountVerificationConfirmAPI,
    UserCreateAPI,
    UserPasswordResetAPI,
    UserPasswordResetConfirmAPI,
)


class TestPublicUsersSerializers:

    #####################
    # Input serializers #
    #####################

    @pytest.mark.django_db
    def test_input_serializer_users_create(self):
        """
        Test input serializer validity of the UserCreateAPI endpoint.
        """

        user = baker.make(User)
        serializer = UserCreateAPI.InputSerializer(data=user.__dict__)

        assert serializer.is_valid()
        assert serializer.data
        assert serializer.errors == {}

    def test_input_serializer_users_account_verification(self):
        """
        Test input serializer validity of the UserAccountVerificationAPI endpoint.
        """

        payload_json = {"email": "somerandomemail@example.com"}
        serializer = UserAccountVerificationAPI.InputSerializer(data=payload_json)

        assert serializer.is_valid()
        assert serializer.data
        assert serializer.errors == {}

    def test_input_serializer_users_account_verification_confirm(self):
        """
        Test input serializer validity of the UserAccountVerificationConfirmAPI endpoint.
        """

        payload_json = {"uid": "some_uid", "token": "some_token"}
        serializer = UserAccountVerificationConfirmAPI.InputSerializer(
            data=payload_json
        )

        assert serializer.is_valid()
        assert serializer.data
        assert serializer.errors == {}

    def test_input_serializer_users_password_reset(self):
        """
        Test input serializer validity of the UserPasswordResetAPI endpoint.
        """

        payload_json = {"email": "somerandomemail@example.com"}
        serializer = UserPasswordResetAPI.InputSerializer(data=payload_json)

        assert serializer.is_valid()
        assert serializer.data
        assert serializer.errors == {}

    def test_input_serializer_users_password_reset_confirm(self):
        """
        Test input serializer validity of the UserPasswordResetConfirmAPI endpoint.
        """

        payload_json = {
            "new_password": "supersecret",
            "uid": "some_uid",
            "token": "some_token",
        }
        serializer = UserPasswordResetConfirmAPI.InputSerializer(data=payload_json)

        assert serializer.is_valid()
        assert serializer.data
        assert serializer.errors == {}

    ######################
    # Output serializers #
    ######################

    # Currently none
