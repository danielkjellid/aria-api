import pytest

from aria.categories.selectors import (
    categories_children_active_list_for_category,
    categories_navigation_active_list,
    categories_parent_active_list,
)
from aria.categories.tests.utils import create_category

pytestmark = pytest.mark.django_db


class TestCategoriesSelectors:
    def test_categories_navigation_list(self):
        pass  # Not converted yet

    def test_categories_navigation_active_list(self, django_assert_max_num_queries):
        """
        Test the selector categories_navigation_active_list returns expected
        response within query limit.
        """

        main_cat_1 = create_category(name="Main cat 1")
        main_cat_1_sub_1 = create_category("Sub cat 1.1", parent=main_cat_1)
        main_cat_1_sub_2 = create_category("Sub cat 1.2", parent=main_cat_1)

        main_cat_2 = create_category(name="Main cat 2")
        main_cat_2_sub_1 = create_category("Sub cat 2.1", parent=main_cat_2)

        # Uses 3 queries: 1 for getting categorues, 1 for getting parents and
        # 1 for getting children.
        with django_assert_max_num_queries(3):
            categories = categories_navigation_active_list()

        assert len(categories) == 2
        assert categories[0].id == main_cat_1.id
        assert categories[0].children[0].id == main_cat_1_sub_1.id
        assert categories[0].children[1].id == main_cat_1_sub_2.id
        assert categories[1].id == main_cat_2.id
        assert categories[1].children[0].id == main_cat_2_sub_1.id

    def test_categories_parent_active_list(self, django_assert_max_num_queries):
        """
        Test the categories_parent_active_list selector returns expected
        response within query limit.
        """

        main_cat_1 = create_category(name="Main cat 1")
        create_category("Sub cat 1.1", parent=main_cat_1)
        create_category("Sub cat 1.2", parent=main_cat_1)

        main_cat_2 = create_category(name="Main cat 2")
        create_category("Sub cat 2.1", parent=main_cat_2)

        # Uses 1 query for getting appropriate parent categories.
        with django_assert_max_num_queries(1):
            parent_categories = categories_parent_active_list()

        assert len(parent_categories) == 2
        assert parent_categories[0].id == main_cat_1.id
        assert parent_categories[1].id == main_cat_2.id

    def test_categories_parents_active_list_for_category(
        self, django_assert_max_num_queries
    ):
        pass

    def test_categories_children_active_list_for_category(
        self, django_assert_max_num_queries
    ):
        """
        Test the categories_children_active_list_for_category
        selector returns expected response within query limit
        for a specific category.
        """

        main_cat_1 = create_category(name="Main cat 1")
        main_cat_1_sub_1 = create_category("Sub cat 1.1", parent=main_cat_1)
        main_cat_1_sub_2 = create_category("Sub cat 1.2", parent=main_cat_1)

        main_cat_2 = create_category(name="Main cat 2")
        main_cat_2_sub_1 = create_category("Sub cat 2.1", parent=main_cat_2)

        # Uses 1 query for getting child categories.
        with django_assert_max_num_queries(1):
            main_cat_1_children = categories_children_active_list_for_category(
                category=main_cat_1
            )

        assert len(main_cat_1_children) == 2
        assert main_cat_1_children[0].id == main_cat_1_sub_1.id
        assert main_cat_1_children[1].id == main_cat_1_sub_2.id

        # Uses 1 query for getting child categories.
        with django_assert_max_num_queries(1):
            main_cat_2_children = categories_children_active_list_for_category(
                category=main_cat_2
            )

        assert len(main_cat_2_children) == 1
        assert main_cat_2_children[0].id == main_cat_2_sub_1.id

    def test_categories_siblings_active_list_for_category(self):
        pass

    def test_category_tree_active_list_for_product(self):
        pass

    def test_category_detail_record(self):
        pass
