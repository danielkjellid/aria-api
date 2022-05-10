import pytest
from model_bakery import baker

from aria.users.models import User
from aria.users.viewsets.public import (
    UserPasswordResetConfirmAPI,
)


class TestPublicUsersSerializers:
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
