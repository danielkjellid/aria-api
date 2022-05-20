from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import Group
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.models import Site

import pytest
from model_bakery import baker

from aria.audit_logs.selectors import logs_for_instance_list
from aria.core.exceptions import ApplicationError
from aria.users.models import User
from aria.users.services import (
    user_create,
    user_set_password,
    user_update,
    user_verify_account,
)

pytestmark = pytest.mark.django_db


class TestUsersServices:
    def test_user_create_creates_user(
        self, unprivileged_user, django_assert_max_num_queries
    ):
        """
        Test that the user_create service creates a user.
        """

        existing_user = unprivileged_user
        group = baker.make(Group)

        # Check if user exist (1), create user (1), get site (1),  add group (1)
        with django_assert_max_num_queries(4):
            new_user = user_create(
                email="test@example.com",
                password="supersecret",
                subscribed_to_newsletter=False,
                send_verification_email=False,
                group=group,
            )

        assert new_user.email == "test@example.com"
        assert new_user.subscribed_to_newsletter is False
        assert new_user.is_staff is False
        assert new_user.is_superuser is False
        assert Group.objects.filter(id=group.id, user__id=new_user.id).exists()

        with pytest.raises(ValueError):
            # Test no provided email
            user_create(
                email="",
                password="supersecret",
                subscribed_to_newsletter=False,
                send_verification_email=False,
            )

        with pytest.raises(ApplicationError):
            # Test user already exists
            user_create(
                email=existing_user.email,
                password="supersecret",
                subscribed_to_newsletter=False,
                send_verification_email=False,
            )

        with pytest.raises(ApplicationError):
            # Test email does does not pass validation.
            user_create(
                email="willnotpass",
                password="supersecret",
                subscribed_to_newsletter=False,
                send_verification_email=False,
            )

        with pytest.raises(ApplicationError):
            # Test password does does not pass validation.
            user_create(
                email="someone@example.com",
                password="1234",
                subscribed_to_newsletter=False,
                send_verification_email=False,
            )

    def test_user_update_updates_user(
        self, unprivileged_user, django_assert_max_num_queries
    ):
        """
        Test that the user_update service updates a user and creates
        appropriate logs.
        """

        author = baker.make(User)
        site = baker.make(Site)
        user = baker.make(User, **{"site": site})

        # Save "old" fields to assert later
        old_user_email = user.email
        old_user_first_name = user.first_name
        old_user_has_confirmed_email = user.has_confirmed_email

        updates = {"email": "updatedemail@example.com"}

        # Get user (1) + site (3), update user (1), create log (1) and since
        # transaction is atomic, it creates and releases savepoint (2)
        with django_assert_max_num_queries(8):
            updated_user = user_update(
                user=user, data=updates, author=author, log_change=True
            )

        created_log_entry = logs_for_instance_list(User, updated_user.id).first()

        # Assert change
        assert updated_user.email == "updatedemail@example.com"

        # Assert that we didn't change any other data
        assert updated_user.first_name == old_user_first_name
        assert updated_user.has_confirmed_email == old_user_has_confirmed_email

        # Assert correct log entry
        assert created_log_entry.change["old_value"] == old_user_email
        assert created_log_entry.change["new_value"] == updated_user.email

    def test_user_verify_account_verifies_account(
        self, unprivileged_user, django_assert_max_num_queries
    ):
        """
        Test that the user_verify_account sets has_confirmed_email = True.
        """

        user = unprivileged_user
        uid = user.uid
        token = user.generate_verification_email_token()

        user.has_confirmed_email = False
        user.save()

        old_email_confirmed_value = user.has_confirmed_email

        # Uses 3 queries: 1 for getting user, 1 for updating user, and
        # 1 for getting site.
        with django_assert_max_num_queries(3):
            updated_user = user_verify_account(uid=uid, token=token)

        assert updated_user.has_confirmed_email is True
        assert updated_user.has_confirmed_email != old_email_confirmed_value

    def test_user_set_password_sets_new_password(
        self, unprivileged_user, django_assert_max_num_queries
    ):
        """
        Test that the user_set_password sets a new password, and that it is
        saved and hashed.
        """
        user = unprivileged_user
        uid = user.uid
        token = default_token_generator.make_token(user)

        # Uses 3 queries: 1 for getting user, 1 for setting password, and
        # 1 for getting site.
        with django_assert_max_num_queries(3):
            updated_user = user_set_password(
                uid=uid, token=token, new_password="horsebatterystaple"
            )

        user_instance = User.objects.get(id=updated_user.id)

        assert check_password("horsebatterystaple", user_instance.password) is True
