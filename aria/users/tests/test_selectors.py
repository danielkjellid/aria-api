import pytest

from aria.users.selectors import user_list
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

        print(user_1.site.name)

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
