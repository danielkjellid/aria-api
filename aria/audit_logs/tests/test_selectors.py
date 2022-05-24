import pytest

from aria.audit_logs.selectors import log_entry_list_for_instance
from aria.audit_logs.tests.utils import create_log_entry
from aria.users.models import User
from aria.users.tests.utils import create_user

pytestmark = pytest.mark.django_db


class TestAuditLogsSelectors:
    def test_log_entry_list_for_instance(self, django_assert_max_num_queries):
        """
        Test the log_entry_list_for_instance selector returns expected response
        within query limit for a specific instance.
        """

        author = create_user(email="author@example.com")
        user_1 = create_user()
        user_2 = create_user(email="user_2@example.com")

        log_entry_1 = create_log_entry(
            User,
            obj_id=user_1.id,
            author=author,
            change_message={
                "field": "email",
                "old_value": "something",
                "new_value": "something else",
            },
        )
        log_entry_2 = create_log_entry(
            User,
            obj_id=user_1.id,
            author=author,
            change_message={
                "field": "first_name",
                "old_value": "something",
                "new_value": "something else",
            },
        )
        log_entry_3 = create_log_entry(
            User,
            obj_id=user_1.id,
            author=author,
            change_message={
                "field": "last_name",
                "old_value": "something",
                "new_value": "something else",
            },
        )
        log_entry_4 = create_log_entry(
            User,
            obj_id=user_2.id,
            author=author,
            change_message={
                "field": "email",
                "old_value": "something",
                "new_value": "something else",
            },
        )

        # Uses 3 queries: Getting notes (1), prefetching author (1) and
        # prefetching the content object (1) in question.
        with django_assert_max_num_queries(3):
            user_1_log_entries = log_entry_list_for_instance(User, id=user_1.id)

        assert len(user_1_log_entries) == 3
        assert user_1_log_entries[0].id == log_entry_3.id
        assert user_1_log_entries[0].change.field == log_entry_3.change["field"]
        assert user_1_log_entries[0].change.old_value == log_entry_3.change["old_value"]
        assert user_1_log_entries[0].change.new_value == log_entry_3.change["new_value"]

        assert user_1_log_entries[1].id == log_entry_2.id
        assert user_1_log_entries[1].change.field == log_entry_2.change["field"]
        assert user_1_log_entries[1].change.old_value == log_entry_2.change["old_value"]
        assert user_1_log_entries[1].change.new_value == log_entry_2.change["new_value"]

        assert user_1_log_entries[2].id == log_entry_1.id
        assert user_1_log_entries[2].change.field == log_entry_1.change["field"]
        assert user_1_log_entries[2].change.old_value == log_entry_1.change["old_value"]
        assert user_1_log_entries[2].change.new_value == log_entry_1.change["new_value"]

        # Uses 3 queries: Getting notes (1), prefetching author (1) and
        # prefetching the content object (1) in question.
        with django_assert_max_num_queries(3):
            user_2_log_entries = log_entry_list_for_instance(User, id=user_2.id)

        assert len(user_2_log_entries) == 1
        assert user_2_log_entries[0].id == log_entry_4.id
        assert user_2_log_entries[0].change.field == log_entry_4.change["field"]
        assert user_2_log_entries[0].change.old_value == log_entry_4.change["old_value"]
        assert user_2_log_entries[0].change.new_value == log_entry_4.change["new_value"]
