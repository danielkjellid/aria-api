import pytest
from model_bakery import baker
from aria.test_utils import model_baker_datetime_formatting
from aria.users.models import User
from aria.users.viewsets.internal import UserListAPI, UserDetailAPI, UserUpdateAPI

pytestmark = pytest.mark.django_db


class TestInternalUsersSerializers:

    #####################
    # Input serializers #
    #####################

    @pytest.mark.django_db
    def test_input_serializer_users_update(self):
        """
        Test input serializer validity of the UserUpdateAPI endpoint.
        """

        user = baker.make(User)

        payload_json = {
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "phone_number": user.formatted_phone_number,
            "has_confirmed_email": user.has_confirmed_email,
            "zip_code": user.zip_code,
            "zip_place": user.zip_place,
            "disabled_emails": user.disabled_emails,
            "subscribed_to_newsletter": user.subscribed_to_newsletter,
            "allow_personalization": user.allow_personalization,
            "allow_third_party_personalization": user.allow_third_party_personalization,
        }

        serializer = UserUpdateAPI.InputSerializer(data=payload_json)

        assert serializer.is_valid(raise_exception=True)
        assert serializer.data
        assert serializer.errors == {}

    def test_input_serializer_users_update_partial(self):
        """
        Test input serializer validity on partial update of the UserUpdateAPI endpoint.
        """

        payload_json = {"email": "somenewemail@example.com"}

        serializer = UserUpdateAPI.InputSerializer(data=payload_json)

        assert serializer.is_valid(raise_exception=True)
        assert serializer.data
        assert serializer.errors == {}

    ######################
    # Output serializers #
    ######################

    @pytest.mark.django_db
    def test_output_serializer_users_list(self):
        """
        Test output serializer validity of the UserListAPI endpoint.
        """

        user = baker.make(User)

        expected_output = {
            "id": user.id,
            "email": user.email,
            "is_active": user.is_active,
            "date_joined": model_baker_datetime_formatting(user.date_joined),
            "profile": {
                "full_name": user.full_name,
                "initial": user.initial,
                "avatar_color": user.avatar_color,
            },
        }
        serializer = UserListAPI.OutputSerializer(user)

        assert serializer.data
        assert serializer.data == expected_output

    @pytest.mark.django_db
    def test_output_serializer_users_detail(self):
        """
        Test output serializer validity of the UserDetailAPI endpoint.
        """

        user = baker.make(User)

        expected_output = {
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

        serializer = UserDetailAPI.OutputSerializer(user)

        assert serializer.data
        assert serializer.data == expected_output
