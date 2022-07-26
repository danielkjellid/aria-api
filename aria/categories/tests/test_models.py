import pytest

from aria.categories.models import Category
from aria.categories.tests.utils import create_category

pytestmark = pytest.mark.django_db


class TestCategoriesModels:
    def test_parent_category_create(self) -> None:
        """
        Test creation of primary category instances
        """

        options = {
            "name": "Parent",
            "slug": "parent",
            "description": "Some basic description",
            "is_active": True,
        }

        category = Category.objects.create(**options)

        # Assert model fields
        assert category.name == "Parent"
        assert category.slug == "parent"
        assert category.description == "Some basic description"
        assert category.ordering == 0  # Default
        assert category.is_active is True

        # Assert that category is a "parent"
        assert category.is_primary is True

    def test_child_category_create(self) -> None:
        """
        Test creation of secondary category instances
        """

        parent_category = create_category()

        options = {
            "name": "Chairs",
            "slug": "chairs",
            "parent": parent_category,
            "description": "Some basic description",
            "is_active": True,
        }

        category = Category.objects.create(**options)

        # Assert model fields
        assert category.name == "Chairs"
        assert category.slug == "chairs"
        assert category.description == "Some basic description"
        assert category.ordering == 0  # Default
        assert category.is_active is True

        # Assert that category is not a "parent" (e.g. has a parent)
        assert category.parent is not None
