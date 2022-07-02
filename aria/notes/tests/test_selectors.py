import pytest

from aria.notes.selectors import note_entry_list_for_instance
from aria.notes.tests.utils import create_note_entry
from aria.products.models import Product
from aria.products.tests.utils import create_product
from aria.users.models import User
from aria.users.tests.utils import create_user

pytestmark = pytest.mark.django_db


class TestNotesSelectors:
    def test_note_entry_list_for_instance(self, django_assert_max_num_queries) -> None:
        """
        Test the note_entry_list_for_instance selector returns expected response
        within query limit for a specific instance.
        """

        user = create_user()
        author = create_user(email="author@example.com")
        note_1 = create_note_entry(
            User, obj_id=user.id, author=author, note="User note 1"
        )
        note_2 = create_note_entry(
            User, obj_id=user.id, author=author, note="User note 2"
        )
        note_3 = create_note_entry(
            User, obj_id=user.id, author=author, note="User note 3"
        )

        product = create_product()
        note_4 = create_note_entry(
            Product, obj_id=product.id, author=author, note="Product note 1"
        )

        # Uses 3 queries: Getting notes (1), prefetching author (1) and
        # prefetching the content object (1) in question.
        with django_assert_max_num_queries(3):
            user_notes = note_entry_list_for_instance(User, pk=user.id)

        assert len(user_notes) == 3
        assert user_notes[0].id == note_3.id
        assert user_notes[0].author_id == note_3.author_id
        assert user_notes[1].id == note_2.id
        assert user_notes[1].author_id == note_2.author_id
        assert user_notes[2].id == note_1.id
        assert user_notes[2].author_id == note_1.author_id

        # Uses 3 queries: Getting notes (1), prefetching author (1) and
        # prefetching the content object (1) in question.
        with django_assert_max_num_queries(3):
            product_notes = note_entry_list_for_instance(Product, pk=product.id)

        assert len(product_notes) == 1
        assert product_notes[0].id == note_4.id
        assert product_notes[0].author_id == note_4.author_id
