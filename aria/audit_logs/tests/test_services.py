import pytest

from aria.audit_logs.services import log_entries_create
from aria.users.tests.utils import create_user

pytestmark = pytest.mark.django_db


class TestAuditLogsServices:
    def test_log_entries_create(self, django_assert_max_num_queries) -> None:
        """
        Test that the log_entries_create service validates input data, throws
        necessary exceptions and creates log within query limit.
        """

        user = create_user()
        author = create_user(email="author@example.com")
        base_change_messages = [
            {
                "field": "email",
                "old_value": user.email,
                "new_value": "someone@example.com",
            },
            {"field": "last_name", "old_value": user.last_name, "new_value": "Griffin"},
        ]

        # Test that ValueError is raised when author is None.
        with pytest.raises(ValueError):
            log_entries_create(
                author=None,
                instance=user,
                change_messages=base_change_messages,
            )

        # Test that ValueError is raised if one of the change dict
        # values are None.
        non_key_val_changes = [
            {
                "field": "email",
                "old_value": user.email,
                "new_value": user.email,
            },
            {"field": None, "old_value": user.last_name, "new_value": "Griffin"},
        ]
        with pytest.raises(ValueError):
            log_entries_create(
                author=author,
                instance=user,
                change_messages=non_key_val_changes,
            )

        # Test that ValueError is raised if one old_value and
        # new_value values are equal.
        equal_values_changes = [
            {
                "field": "email",
                "old_value": user.email,
                "new_value": user.email,
            },
            {"field": "last_name", "old_value": user.last_name, "new_value": "Griffin"},
        ]
        with pytest.raises(ValueError):
            log_entries_create(
                author=author,
                instance=user,
                change_messages=equal_values_changes,
            )

        # Test that fields with reverse relations are not logged.
        reverse_rels_changes = [
            {
                "field": "note_entries",
                "old_value": "something",
                "new_value": "something else",
            }
        ]

        with django_assert_max_num_queries(0):
            reverse_rels_logs = log_entries_create(
                author=author, instance=user, change_messages=reverse_rels_changes
            )

        assert len(reverse_rels_logs) == 0

        # Test that fields that does not exist on the model are not
        # logged.
        non_existant_field_changes = [
            {
                "field": "price",
                "old_value": 500,
                "new_value": 499,
            }
        ]

        with django_assert_max_num_queries(0):
            non_existant_field_logs = log_entries_create(
                author=author, instance=user, change_messages=non_existant_field_changes
            )

        assert len(non_existant_field_logs) == 0

        # Test that creating logs works as expected with the correct data.
        # Uses 2 queries: 1 for getting content type, and 1 for bulk creating logs.
        with django_assert_max_num_queries(2):
            logs_created = log_entries_create(
                author=author, instance=user, change_messages=base_change_messages
            )

        assert len(logs_created) == 2
        assert logs_created[0].change.field == base_change_messages[0]["field"]
        assert logs_created[0].change.old_value == base_change_messages[0]["old_value"]
        assert logs_created[0].change.new_value == base_change_messages[0]["new_value"]
        assert logs_created[1].change.field == base_change_messages[1]["field"]
        assert logs_created[1].change.old_value == base_change_messages[1]["old_value"]
        assert logs_created[1].change.new_value == base_change_messages[1]["new_value"]
