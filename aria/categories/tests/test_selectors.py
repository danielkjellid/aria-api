import pytest

from aria.categories.schemas.records import CategoryDetailRecord, CategoryRecord
from aria.categories.selectors import categories_navigation_active_list
from aria.categories.tests.utils import create_category

pytestmark = pytest.mark.django_db


class TestCategoriesSelectors:
    def test_categories_navigation_list(self):
        pass  # Not converted yet

    def test_categories_navigation_active_list(self, django_assert_max_num_queries):
        main_cat_1 = create_category(name="Main cat 1")
        main_cat_1_sub_1 = create_category("Sub cat 1.1", parent=main_cat_1)
        main_cat_1_sub_2 = create_category("Sub cat 1.2", parent=main_cat_1)

        main_cat_2 = create_category(name="Main cat 2")
        main_cat_2_sub_1 = create_category("Sub cat 2.1", parent=main_cat_2)

        expected_output = [
            CategoryDetailRecord(
                id=main_cat_1.id,
                name=main_cat_1.name,
                slug=main_cat_1.slug,
                description=main_cat_1.description,
                ordering=main_cat_1.ordering,
                parent=main_cat_1.parent_id,
                parents=[],
                children=[
                    CategoryRecord(
                        id=main_cat_1_sub_1.id,
                        name=main_cat_1_sub_1.name,
                        slug=main_cat_1_sub_1.slug,
                        ordering=main_cat_1_sub_1.ordering,
                        parent=main_cat_1_sub_1.parent_id,
                    ),
                    CategoryRecord(
                        id=main_cat_1_sub_2.id,
                        name=main_cat_1_sub_2.name,
                        slug=main_cat_1_sub_2.slug,
                        ordering=main_cat_1_sub_2.ordering,
                        parent=main_cat_1_sub_2.parent_id,
                    ),
                ],
            ),
            CategoryDetailRecord(
                id=main_cat_2.id,
                name=main_cat_2.name,
                slug=main_cat_2.slug,
                description=main_cat_2.description,
                ordering=main_cat_2.ordering,
                parent=main_cat_2.parent_id,
                parents=[],
                children=[
                    CategoryRecord(
                        id=main_cat_2_sub_1.id,
                        name=main_cat_2_sub_1.name,
                        slug=main_cat_2_sub_1.slug,
                        ordering=main_cat_2_sub_1.ordering,
                        parent=main_cat_2_sub_1.parent_id,
                    ),
                ],
            ),
        ]

        with django_assert_max_num_queries(3):
            categories = categories_navigation_active_list()

        assert categories == expected_output

    def test_categories_parent_active_list(self):
        pass  # Not converted yet

    def test_categories_parents_active_list_for_category(self):
        pass

    def test_categories_children_active_list_for_category(self):
        pass

    def test_categories_siblings_active_list_for_category(self):
        pass

    def test_category_tree_active_list_for_product(self):
        pass

    def test_category_record(self):
        pass
