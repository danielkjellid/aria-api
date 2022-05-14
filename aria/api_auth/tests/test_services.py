from datetime import timedelta
from uuid import uuid4

from django.utils import timezone

import pytest

from aria.api_auth.exceptions import TokenError
from aria.api_auth.models import BlacklistedToken, OutstandingToken
from aria.api_auth.records import TokenPayload
from aria.api_auth.selectors import _token_decode
from aria.api_auth.services import (
    _access_token_create_and_encode,
    _refresh_token_create_and_encode,
    refresh_token_blacklist,
    token_pair_obtain_for_unauthenticated_user,
    token_pair_obtain_for_user,
    token_pair_obtain_new_from_refresh_token,
)
from aria.api_auth.utils import datetime_to_epoch
from aria.core.exceptions import ApplicationError

pytestmark = pytest.mark.django_db


class TestAPIAuthServices:
    def test__refresh_token_create_and_encode(
        self, django_assert_max_num_queries, unprivileged_user
    ):
        """
        Test that the _refresh_token_create_and_encode service replaces
        needed default, encodes a token, and creates an entry in the
        OutstandingToken table.
        """

        user = unprivileged_user

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

    def test__access_token_create_and_encode(
        self, django_assert_max_num_queries, unprivileged_user
    ):
        """
        Test that the _access_token_create_and_encode service replaces
        needed default and encodes a token.
        """

        user = unprivileged_user

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

    def test_token_pair_obtain_for_user(
        self, django_assert_max_num_queries, mocker, unprivileged_user
    ):
        """
        Test that token_pair_obtain_for_user calls the needed
        services to produce a valid access and refresh token
        as well that it does not exceed max allowed queries.
        """

        user = unprivileged_user

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
        self, django_assert_max_num_queries, mocker, unprivileged_user
    ):
        user = unprivileged_user
        user.set_password("supersecretpassword")
        user.save()

        token_pair_obtain_for_user_mock = mocker.patch(
            "aria.api_auth.services.token_pair_obtain_for_user"
        )

        # Service calls token_pair_obtain_for_user, which again
        # calls _refresh_token_create_and_encode which creates a
        # db entry + 1 for looking up user and + 1 for looking up
        # site.
        with django_assert_max_num_queries(3):
            token_pair = token_pair_obtain_for_unauthenticated_user(
                email="testuser@example.com", password="supersecretpassword"
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

    def test_token_pair_obtain_new_from_refresh_token_invalid_token(
        self,
        django_assert_max_num_queries,
        mocker,
        refresh_token_payload,
        unprivileged_user,
        encode_token,
    ):
        """
        Test how the token_pair_obtain_new_from_refresh_token service
        reacts to getting an invalid token.
        """

        user = unprivileged_user

        refresh_payload = refresh_token_payload(user_id=user.id)

        invalid_token = encode_token(refresh_payload)

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

        # Check that an invalid token is not validated.
        with pytest.raises(TokenError):
            with django_assert_max_num_queries(0):
                token_pair_obtain_new_from_refresh_token(invalid_token)

        assert refresh_token_is_valid_mock.call_count == 1
        assert refresh_token_is_valid_mock.call_args_list[0].args[0] == invalid_token
        assert (
            token_pair_obtain_for_user_mock.call_count == 0
        )  # Should throw exception before this

    def test_token_pair_obtain_new_from_refresh_token_invalid_user(
        self,
        django_assert_max_num_queries,
        mocker,
        settings,
        refresh_token_payload,
        encode_token,
    ):
        """
        Test how token_pair_obtain_new_from_refresh_token responds
        to getting a valid token, but with a jti that does not bellong
        to the user.
        """

        refresh_payload = refresh_token_payload(user_id=999)

        valid_token_invalid_user = encode_token(refresh_payload)
        decoded_valid_token_invalid_user = _token_decode(valid_token_invalid_user)

        refresh_token_is_valid_mock = mocker.patch(
            "aria.api_auth.services.refresh_token_is_valid",
            return_value=(
                None,
                TokenPayload(
                    token_type=decoded_valid_token_invalid_user.token_type,
                    exp=decoded_valid_token_invalid_user.exp,
                    iat=decoded_valid_token_invalid_user.iat,
                    jti=decoded_valid_token_invalid_user.jti,
                    iss=decoded_valid_token_invalid_user.iss,
                    user_id=decoded_valid_token_invalid_user.user_id,
                ),
            ),
        )
        token_pair_obtain_for_user_mock = mocker.patch(
            "aria.api_auth.services.token_pair_obtain_for_user"
        )

        # Check that service throws exception if the user does not exist.
        with pytest.raises(TokenError):
            with django_assert_max_num_queries(0):
                token_pair_obtain_new_from_refresh_token(valid_token_invalid_user)

        assert refresh_token_is_valid_mock.call_count == 1
        assert (
            refresh_token_is_valid_mock.call_args_list[0].args[0]
            == valid_token_invalid_user
        )
        assert (
            token_pair_obtain_for_user_mock.call_count == 0
        )  # Should throw exception before this

    def test_token_pair_obtain_new_from_refresh_token_valid_token(
        self,
        django_assert_max_num_queries,
        mocker,
        refresh_token_payload,
        unprivileged_user,
    ):
        """
        Test that the token_pair_obtain_new_from_refresh_token returns
        a new valid token pair when provided a valid refresh token.
        """

        user = unprivileged_user

        refresh_payload = refresh_token_payload(user_id=user.id)

        valid_token = _refresh_token_create_and_encode(refresh_payload)
        decoded_valid_token = _token_decode(valid_token)

        refresh_token_is_valid_mock = mocker.patch(
            "aria.api_auth.services.refresh_token_is_valid",
            return_value=(
                True,
                TokenPayload(
                    token_type=decoded_valid_token.token_type,
                    exp=decoded_valid_token.exp,
                    iat=decoded_valid_token.iat,
                    jti=decoded_valid_token.jti,
                    iss=decoded_valid_token.iss,
                    user_id=decoded_valid_token.user_id,
                ),
            ),
        )
        token_pair_obtain_for_user_mock = mocker.patch(
            "aria.api_auth.services.token_pair_obtain_for_user"
        )

        # 1 for getting the user object from token user_id.
        with django_assert_max_num_queries(1):
            new_tokens = token_pair_obtain_new_from_refresh_token(valid_token)

        assert refresh_token_is_valid_mock.call_count == 1
        assert refresh_token_is_valid_mock.call_args_list[0].args[0] == valid_token
        assert token_pair_obtain_for_user_mock.call_count == 1
        assert token_pair_obtain_for_user_mock.call_args_list[0].args[0] == user
        assert new_tokens.refresh_token is not None
        assert new_tokens.access_token is not None

    def test_refresh_token_blacklist_invalid_token(
        self,
        django_assert_max_num_queries,
        mocker,
        refresh_token_payload,
        unprivileged_user,
        encode_token,
    ):
        """
        Test that the refresh_token_blacklist service raises an
        exception appropriately.
        """

        user = unprivileged_user

        refresh_payload = refresh_token_payload(user_id=user.id)

        invalid_token = encode_token

        refresh_token_is_valid_mock = mocker.patch(
            "aria.api_auth.services.refresh_token_is_valid",
            return_value=(
                False,
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

        # Sanity check that we're in a good state with 0 blacklisted
        # tokens before checking again after the service has run.
        assert BlacklistedToken.objects.all().count() == 0

        # Check that an invalid token is not validated.
        with pytest.raises(TokenError):
            with django_assert_max_num_queries(0):
                refresh_token_blacklist(invalid_token)

        assert refresh_token_is_valid_mock.call_count == 1
        assert refresh_token_is_valid_mock.call_args_list[0].args[0] == invalid_token
        # Assert that there is still 0 blacklisted tokens.
        assert BlacklistedToken.objects.all().count() == 0

    def test_refresh_token_blacklist_valid_token(
        self,
        django_assert_max_num_queries,
        mocker,
        refresh_token_payload,
        unprivileged_user,
    ):
        """
        Test that the refresh_token_blacklist blacklists refresh
        token on valid token provided.
        """

        user = unprivileged_user

        refresh_payload = refresh_token_payload(user_id=user.id)

        valid_token = _refresh_token_create_and_encode(refresh_payload)
        decoded_valid_token = _token_decode(valid_token)

        refresh_token_is_valid_mock = mocker.patch(
            "aria.api_auth.services.refresh_token_is_valid",
            return_value=(
                True,
                TokenPayload(
                    token_type=decoded_valid_token.token_type,
                    exp=decoded_valid_token.exp,
                    iat=decoded_valid_token.iat,
                    jti=decoded_valid_token.jti,
                    iss=decoded_valid_token.iss,
                    user_id=decoded_valid_token.user_id,
                ),
            ),
        )

        # Sanity check that we're in a good state with 0 blacklisted
        # tokens before checking again after the service has run.
        assert BlacklistedToken.objects.all().count() == 0

        # 1 for getting the user object from token user_id.
        with django_assert_max_num_queries(2):
            refresh_token_blacklist(valid_token)

        assert refresh_token_is_valid_mock.call_count == 1
        assert refresh_token_is_valid_mock.call_args_list[0].args[0] == valid_token
        # Check that we created an instance blacklisting the token,
        # and that the token we blacklisted is the one passed in to
        # the serivce.
        assert BlacklistedToken.objects.all().count() == 1
        assert (
            BlacklistedToken.objects.filter(
                token__jti=decoded_valid_token.jti,
                token__user_id=decoded_valid_token.user_id,
            ).count()
            == 1
        )
