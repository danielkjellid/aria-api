import pytest

from aria.users.records import UserProfileRecord, UserRecord
from aria.users.selectors import user_detail, user_list
from aria.users.tests.utils import create_user

pytestmark = pytest.mark.django_db


class TestUsersSelectors:
    def test_user_list(self, django_assert_max_num_queries) -> None:
        """
        Test that the user_list selector returns appropriate results
        when filters are provided.
        """

        user_1 = create_user(
            email="user_1@example.com",
            phone_number="12345678",
            first_name="First",
            last_name="User",
        )
        user_2 = create_user(
            email="user_2@example.com",
            phone_number="87651234",
            first_name="Second",
            last_name="User",
        )
        user_3 = create_user(
            email="user_3@example.com",
            phone_number="12121212",
            first_name="Third",
            last_name="User",
        )
        user_4 = create_user(
            email="user_4@example.com",
            phone_number="12345678",
            first_name="Fourth",
            last_name="Person",
        )

        # Test email filter
        with django_assert_max_num_queries(1):
            users = user_list(filters={"email": "user_1@example.com"})

        assert len(users) == 1
        assert users[0].id == user_1.id

        # Test phone number filter
        with django_assert_max_num_queries(1):
            users = user_list(filters={"phone_number": "87651234"})

        assert len(users) == 1
        assert users[0].id == user_2.id

        # Test first name filter
        with django_assert_max_num_queries(1):
            users = user_list(filters={"first_name": "Third"})

        assert len(users) == 1
        assert users[0].id == user_3.id

        # Test last name filter
        with django_assert_max_num_queries(1):
            users = user_list(filters={"last_name": "User"})

        assert len(users) == 3  # All users except last has the same last name
        assert user_4.id not in sorted(users, key=lambda u: u.id)

    def test_selector_user_detail(self, django_assert_max_num_queries) -> None:
        """
        Test that the user_detail selector returns expected output withing query
        limits.
        """

        user = create_user()

        with django_assert_max_num_queries(1):
            fetched_user = user_detail(pk=user.pk)

        assert fetched_user == UserRecord(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            profile=UserProfileRecord(
                full_name=user.full_name,
                initial=user.initial,
                avatar_color=user.avatar_color,
            ),
            birth_date=user.birth_date,
            phone_number=user.phone_number,
            has_confirmed_email=user.has_confirmed_email,
            street_address=user.street_address,
            zip_code=user.zip_code,
            zip_place=user.zip_place,
            disabled_emails=user.disabled_emails,
            subscribed_to_newsletter=user.subscribed_to_newsletter,
            allow_personalization=user.allow_personalization,
            allow_third_party_personalization=user.allow_third_party_personalization,
            acquisition_source=user.acquisition_source,
            date_joined=user.date_joined,
            is_active=user.is_active,
            is_staff=user.is_staff,
            is_superuser=user.is_superuser,
            permissions=[],
        )
