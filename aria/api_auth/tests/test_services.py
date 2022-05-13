import pytest
from django.utils import timezone
from model_bakery import baker
from aria.users.models import User
from aria.api_auth.services import (
    _refresh_token_create_and_encode,
    _access_token_create_and_encode,
    token_pair_obtain_for_user,
    token_pair_obtain_for_unauthenticated_user,
    token_pair_obtain_new_from_refresh_token,
    refresh_token_blacklist,
)
from aria.api_auth.selectors import _token_decode
from aria.api_auth.models import OutstandingToken
from aria.core.exceptions import ApplicationError
from aria.api_auth.records import TokenPayload
from aria.api_auth.utils import datetime_to_epoch
from django.contrib.sites.models import Site
from django.utils import timezone
from datetime import timedelta
from uuid import uuid4
import jwt

pytestmark = pytest.mark.django_db


class TestApiAuthServices:
    def test__refresh_token_create_and_encode(self, django_assert_max_num_queries):
        """
        Test that the _refresh_token_create_and_encode service replaces
        needed default, encodes a token, and creates an entry in the
        OutstandingToken table.
        """

        user = baker.make("users.User")

        payload = {
            "token_type": None,
            "exp": None,
            "iat": timezone.now(),
            "jti": None,
            "iss": "api.flis.no",
            "user_id": user.id,
        }

        # 1 query for creating a new OutstandingToken object.
        with django_assert_max_num_queries(1):
            encoded_refresh_token = _refresh_token_create_and_encode(payload)

        decoded_token = _token_decode(encoded_refresh_token)

        # Make sure serivce has changed defaults.
        assert decoded_token.token_type == "refresh"
        assert decoded_token.exp is not None
        assert decoded_token.jti is not None

        # Check that non defaults is not changed.
        assert decoded_token.user_id == user.id
        assert decoded_token.iss == "api.flis.no"

        token = OutstandingToken.objects.filter(
            jti=decoded_token.jti, user_id=decoded_token.user_id
        )
        # Check that object was created in db.
        assert token.exists()
        assert len(token) == 1

    def test__access_token_create_and_encode(self, django_assert_max_num_queries):
        """
        Test that the _access_token_create_and_encode service replaces
        needed default and encodes a token.
        """

        user = baker.prepare("users.User")

        payload = {
            "token_type": None,
            "exp": None,
            "iat": timezone.now(),
            "jti": None,
            "iss": "api.flis.no",
            "user_id": user.id,
        }

        # The access token is not stored in the db, so we do
        # not need any queries for this.
        with django_assert_max_num_queries(0):
            encoded_access_token = _access_token_create_and_encode(payload)

        decoded_token = _token_decode(encoded_access_token)

        # Make sure serivce has changed defaults.
        assert decoded_token.token_type == "access"
        assert decoded_token.exp is not None
        assert decoded_token.jti is not None

        # Check that non defaults is not changed.
        assert decoded_token.user_id == user.id
        assert decoded_token.iss == "api.flis.no"

    def test_token_pair_obtain_for_user(self, django_assert_max_num_queries, mocker):
        """
        Test that token_pair_obtain_for_user calls the needed
        services to produce a valid access and refresh token
        as well that it does not exceed max allowed queries.
        """

        user = baker.prepare("users.User")

        refresh_token_create_and_encode_mock = mocker.patch(
            "aria.api_auth.services._refresh_token_create_and_encode",
            return_value="supersecretrefresh",
        )
        access_token_create_and_encode_mock = mocker.patch(
            "aria.api_auth.services._access_token_create_and_encode",
            return_value="supersecretaccess",
        )

        # Uses _refresh_token_create_and_encode, which creates a
        # single db entry.
        with django_assert_max_num_queries(1):
            token_pair = token_pair_obtain_for_user(user)

        # Assert that the internal services are called.
        assert refresh_token_create_and_encode_mock.call_count == 1
        assert access_token_create_and_encode_mock.call_count == 1

        # Assert that returned pair is actually populated.
        assert token_pair.refresh_token is not None
        assert token_pair.access_token is not None

    def test_token_pair_obtain_for_unauthenticated_user(
        self, django_assert_max_num_queries, mocker, settings
    ):
        # User must have a site, and that site must be active for us to
        # be able to authenticate.
        site = Site.objects.create(domain="test.example.com", name="Test")
        settings.SITE_ID = site.id

        user = baker.make(User, **{"email": "user@example.com"})
        user.set_password("supersecretpassword")
        user.site = site
        user.save()

        token_pair_obtain_for_user_mock = mocker.patch(
            "aria.api_auth.services.token_pair_obtain_for_user"
        )

        # Service calls token_pair_obtain_for_user, which again
        # calls _refresh_token_create_and_encode which creates a
        # db entry + 1 for looking up user and + for looking up
        # site.
        with django_assert_max_num_queries(2):
            token_pair = token_pair_obtain_for_unauthenticated_user(
                email="user@example.com", password="supersecretpassword"
            )

        # Assert that service creating tokens is called with correct
        # args.
        assert token_pair_obtain_for_user_mock.call_count == 1
        assert token_pair_obtain_for_user_mock.call_args_list[0].args[0] == user

        # Assert that returned pair is actually populated.
        assert token_pair.refresh_token is not None
        assert token_pair.access_token is not None

        # Assert that wrong credentials throws exception.
        with pytest.raises(ApplicationError):
            token_pair_obtain_for_unauthenticated_user(
                email="doesnotexist@example.com", password="supersecret"
            )

    def test_token_pair_obtain_new_from_refresh_token(
        self, django_assert_max_num_queries, mocker, settings
    ):

        user = baker.make("users.User")

        refresh_payload = {
            "token_type": "refresh",
            "exp": timezone.now() + timedelta(days=14),
            "iat": timezone.now(),
            "jti": uuid4().hex,
            "iss": "api.flis.no",
            "user_id": user.id,
        }

        refresh_token_is_valid_mock = mocker.patch(
            "aria.api_auth.services.refresh_token_is_valid",
            return_value=(
                None,
                TokenPayload(
                    token_type="refresh",
                    exp=datetime_to_epoch((timezone.now() + timedelta(days=14))),
                    iat=datetime_to_epoch(timezone.now()),
                    jti=uuid4().hex,
                    iss="api.flis.no",
                    user_id=user.id,
                ),
            ),
        )
        token_pair_obtain_for_user_mock = mocker.patch(
            "aria.api_auth.services.token_pair_obtain_for_user"
        )

        invalid_token = jwt.encode(
            refresh_payload, "notvalidsigningkey", algorithm="HS256"
        )

        # Check that an invalid token is not validated.
        with pytest.raises(ApplicationError):
            # There should be no DB calls for validation refresh token.
            with django_assert_max_num_queries(0):
                token_pair_obtain_new_from_refresh_token(invalid_token)

        assert refresh_token_is_valid_mock.call_count == 1
        assert refresh_token_is_valid_mock.call_args_list[0].args[0] == invalid_token
        assert (
            token_pair_obtain_for_user_mock.call_count == 0
        )  # Should throw exception before this

        refresh_payload["user_id"] = 999
        valid_token_invalid_user = jwt.encode(
            refresh_payload, settings.JWT_SIGNING_KEY, algorithm="HS256"
        )

        # Check that service throws exception if the user does not exist.
        with pytest.raises(ApplicationError):
            # TODO: comment
            with django_assert_max_num_queries(0):
                token_pair_obtain_new_from_refresh_token(valid_token_invalid_user)

        assert refresh_token_is_valid_mock.call_count == 2
        assert (
            refresh_token_is_valid_mock.call_args_list[0].args[0]
            == valid_token_invalid_user
        )
        assert (
            token_pair_obtain_for_user_mock.call_count == 0
        )  # Should throw exception before this

        refresh_payload["user_id"] = user.id
        valid_token = _refresh_token_create_and_encode(refresh_payload)

        with django_assert_max_num_queries(0):
            token_pair_obtain_new_from_refresh_token(valid_token)

        assert refresh_token_is_valid_mock.call_count == 3
        assert refresh_token_is_valid_mock.call_args_list[0].args[0] == valid_token
        assert token_pair_obtain_for_user_mock == 1
        assert token_pair_obtain_for_user_mock.call_args_list[0].args[0] == user

    def test_refresh_token_blacklist(self, django_assert_max_num_queries, mocker):
        pass
