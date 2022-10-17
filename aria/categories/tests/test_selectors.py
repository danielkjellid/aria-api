import pytest

from aria.categories.records import CategoryDetailRecord, CategoryRecord
from aria.categories.selectors import (
    category_children_active_list_for_category,
    category_detail_record,
    category_navigation_active_list,
    category_parent_active_list,
    category_parents_active_list_for_category,
    category_tree_active_list_for_product,
)
from aria.categories.tests.utils import create_category
from aria.core.records import BaseHeaderImageRecord, BaseListImageRecord
from aria.products.models import Product
from aria.products.tests.utils import create_product

pytestmark = pytest.mark.django_db


class TestCategoriesSelectors:
    def test_category_navigation_active_list(
        self, django_assert_max_num_queries
    ) -> None:
        """
        Test the selector category_navigation_active_list returns expected
        response within query limit.
        """

        main_cat_1 = create_category(name="Main cat 1")
        main_cat_1_sub_1 = create_category("Sub cat 1.1", parent=main_cat_1)
        main_cat_1_sub_2 = create_category("Sub cat 1.2", parent=main_cat_1)

        main_cat_2 = create_category(name="Main cat 2")
        main_cat_2_sub_1 = create_category("Sub cat 2.1", parent=main_cat_2)

        # Uses 3 queries: 1 for getting categories, 1 for getting parents and
        # 1 for getting children.
        with django_assert_max_num_queries(3):
            categories = category_navigation_active_list()

        assert len(categories) == 2
        assert categories[0].id == main_cat_1.id
        assert categories[0].children[0].id == main_cat_1_sub_1.id
        assert categories[0].children[1].id == main_cat_1_sub_2.id
        assert categories[1].id == main_cat_2.id
        assert categories[1].children[0].id == main_cat_2_sub_1.id

    def test_category_parent_active_list(self, django_assert_max_num_queries) -> None:
        """
        Test the category_parent_active_list selector returns expected
        response within query limit.
        """

        main_cat_1 = create_category(name="Main cat 1")
        create_category("Sub cat 1.1", parent=main_cat_1)
        create_category("Sub cat 1.2", parent=main_cat_1)

        main_cat_2 = create_category(name="Main cat 2")
        create_category("Sub cat 2.1", parent=main_cat_2)

        # Uses 1 query for getting appropriate parent categories.
        with django_assert_max_num_queries(1):
            parent_categories = category_parent_active_list()

        assert len(parent_categories) == 2
        assert parent_categories[0].id == main_cat_1.id
        assert parent_categories[1].id == main_cat_2.id

    def test_category_parents_active_list_for_category(
        self, django_assert_max_num_queries
    ) -> None:
        """
        Test the category_parents_active_list_for_category
        selector returns expected response within query limit
        for a specific category.
        """

        main_cat_1 = create_category(name="Category 1")
        main_cat_1_sub_cat_1 = create_category("Category 1.1", parent=main_cat_1)

        # Uses 1 query to get categories and parents.
        with django_assert_max_num_queries(1):
            parents_main_cat_1_sub_cat_1 = category_parents_active_list_for_category(
                category=main_cat_1_sub_cat_1
            )

        assert len(parents_main_cat_1_sub_cat_1) == 1
        assert parents_main_cat_1_sub_cat_1[0].id == main_cat_1.id

    def test_category_children_active_list_for_category(
        self, django_assert_max_num_queries
    ) -> None:
        """
        Test the category_children_active_list_for_category
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
            main_cat_1_children = category_children_active_list_for_category(
                category=main_cat_1
            )

        assert len(main_cat_1_children) == 2
        assert main_cat_1_children[0].id == main_cat_1_sub_1.id
        assert main_cat_1_children[1].id == main_cat_1_sub_2.id

        # Uses 1 query for getting child categories.
        with django_assert_max_num_queries(1):
            main_cat_2_children = category_children_active_list_for_category(
                category=main_cat_2
            )

        assert len(main_cat_2_children) == 1
        assert main_cat_2_children[0].id == main_cat_2_sub_1.id

    def test_category_tree_active_list_for_product(
        self, django_assert_max_num_queries
    ) -> None:
        """
        Test the category_tree_active_list_for_product selector returns
        expected response within query limit for a specific product.
        """
        cat_1 = create_category(name="Category")
        subcat_1 = create_category(name="Subcategory 1", parent=cat_1)
        subcat_2 = create_category(name="Subcategory 2", parent=cat_1)

        product = create_product()
        product.categories.set([subcat_1, subcat_2])

        # Test without prefetching first.
        # Uses 3 queries: 1 for getting product category, 1 for getting parents,
        # and 1 for getting children.
        with django_assert_max_num_queries(3):
            category_tree = category_tree_active_list_for_product(product=product)

        sorted_category_tree = sorted(category_tree, key=lambda c: c.id)

        assert len(sorted_category_tree) == 2  # The two subcategories.
        assert sorted_category_tree[0].id == subcat_1.id
        assert sorted_category_tree[1].id == subcat_2.id

        prefetched_product = (
            Product.objects.filter(id=product.id).with_active_categories().first()
        )

        # Test without prefetching first.
        # Uses 2 queries: 1 for getting parents and 1 for getting children.
        with django_assert_max_num_queries(2):
            prefetched_category_tree = category_tree_active_list_for_product(
                product=prefetched_product
            )

        sorted_prefetched_category_tree = sorted(
            prefetched_category_tree, key=lambda c: c.id
        )

        assert len(sorted_prefetched_category_tree) == 2
        assert sorted_prefetched_category_tree[0].id == subcat_1.id
        assert sorted_prefetched_category_tree[1].id == subcat_2.id

    def test_category_detail_record(self, django_assert_max_num_queries) -> None:
        """
        Test the category_detail_record selector returns expected response
        within query limit for a specific category.
        """

        cat_1 = create_category(name="Parent")
        subcat_1 = create_category(name="Child 1", parent=cat_1)
        subcat_2 = create_category(name="Child 2", parent=cat_1)
        subcat_3 = create_category(name="Child 3", parent=cat_1)

        expected_parent_output = CategoryDetailRecord(
            id=cat_1.id,
            name=cat_1.name,
            display_name=cat_1.get_category_display(),
            ordering=cat_1.ordering,
            slug=cat_1.slug,
            description=cat_1.description,
            parent=None,
            parents=[],
            children=[
                CategoryRecord(
                    id=subcat_1.id,
                    name=subcat_1.name,
                    display_name=subcat_1.get_category_display(),
                    slug=subcat_1.slug,
                    description=subcat_1.description,
                    ordering=subcat_1.ordering,
                    parent=subcat_1.parent_id,
                    images=BaseHeaderImageRecord(
                        apply_filter=subcat_1.apply_filter,
                        image_512x512=subcat_1.image_512x512.url,
                        image_640x275=subcat_1.image_640x275.url,
                        image_1024x575=subcat_1.image_1024x575.url,
                        image_1024x1024=subcat_1.image_1024x1024.url,
                        image_1536x860=subcat_1.image_1536x860.url,
                        image_2048x1150=subcat_1.image_2048x1150.url,
                    ),
                    list_images=BaseListImageRecord(
                        image500x305=subcat_1.image500x305.url,
                        image600x440=subcat_1.image600x440.url,
                        image850x520=subcat_1.image850x520.url,
                    ),
                ),
                CategoryRecord(
                    id=subcat_2.id,
                    name=subcat_2.name,
                    display_name=subcat_2.get_category_display(),
                    slug=subcat_2.slug,
                    description=subcat_2.description,
                    ordering=subcat_2.ordering,
                    parent=subcat_2.parent_id,
                    images=BaseHeaderImageRecord(
                        apply_filter=subcat_2.apply_filter,
                        image_512x512=subcat_2.image_512x512.url,
                        image_640x275=subcat_2.image_640x275.url,
                        image_1024x575=subcat_2.image_1024x575.url,
                        image_1024x1024=subcat_2.image_1024x1024.url,
                        image_1536x860=subcat_2.image_1536x860.url,
                        image_2048x1150=subcat_2.image_2048x1150.url,
                    ),
                    list_images=BaseListImageRecord(
                        image500x305=subcat_2.image500x305.url,
                        image600x440=subcat_2.image600x440.url,
                        image850x520=subcat_2.image850x520.url,
                    ),
                ),
                CategoryRecord(
                    id=subcat_3.id,
                    name=subcat_3.name,
                    display_name=subcat_3.get_category_display(),
                    slug=subcat_3.slug,
                    description=subcat_3.description,
                    ordering=subcat_3.ordering,
                    parent=subcat_3.parent_id,
                    images=BaseHeaderImageRecord(
                        apply_filter=subcat_3.apply_filter,
                        image_512x512=subcat_3.image_512x512.url,
                        image_640x275=subcat_3.image_640x275.url,
                        image_1024x575=subcat_3.image_1024x575.url,
                        image_1024x1024=subcat_3.image_1024x1024.url,
                        image_1536x860=subcat_3.image_1536x860.url,
                        image_2048x1150=subcat_3.image_2048x1150.url,
                    ),
                    list_images=BaseListImageRecord(
                        image500x305=subcat_3.image500x305.url,
                        image600x440=subcat_3.image600x440.url,
                        image850x520=subcat_3.image850x520.url,
                    ),
                ),
            ],
            images=BaseHeaderImageRecord(
                apply_filter=cat_1.apply_filter,
                image_512x512=cat_1.image_512x512.url,
                image_640x275=cat_1.image_640x275.url,
                image_1024x575=cat_1.image_1024x575.url,
                image_1024x1024=cat_1.image_1024x1024.url,
                image_1536x860=cat_1.image_1536x860.url,
                image_2048x1150=cat_1.image_2048x1150.url,
            ),
            list_images=BaseListImageRecord(
                image500x305=cat_1.image500x305.url,
                image600x440=cat_1.image600x440.url,
                image850x520=cat_1.image850x520.url,
            ),
        )

        # Test category with children, and no parent.
        # Uses 1 query for getting category.
        with django_assert_max_num_queries(1):
            cat_1_detail_record = category_detail_record(category=cat_1)

        assert cat_1_detail_record == expected_parent_output

        expected_child_output = CategoryDetailRecord(
            id=subcat_1.id,
            name=subcat_1.name,
            display_name=subcat_1.get_category_display(),
            ordering=subcat_1.ordering,
            slug=subcat_1.slug,
            description=subcat_1.description,
            parent=subcat_1.parent_id,
            parents=[
                CategoryRecord(
                    id=cat_1.id,
                    name=cat_1.name,
                    display_name=cat_1.get_category_display(),
                    slug=cat_1.slug,
                    description=cat_1.description,
                    ordering=cat_1.ordering,
                    parent=None,
                    images=BaseHeaderImageRecord(
                        apply_filter=cat_1.apply_filter,
                        image_512x512=cat_1.image_512x512.url,
                        image_640x275=cat_1.image_640x275.url,
                        image_1024x575=cat_1.image_1024x575.url,
                        image_1024x1024=cat_1.image_1024x1024.url,
                        image_1536x860=cat_1.image_1536x860.url,
                        image_2048x1150=cat_1.image_2048x1150.url,
                    ),
                    list_images=BaseListImageRecord(
                        image500x305=cat_1.image500x305.url,
                        image600x440=cat_1.image600x440.url,
                        image850x520=cat_1.image850x520.url,
                    ),
                )
            ],
            children=[],
            images=BaseHeaderImageRecord(
                apply_filter=subcat_1.apply_filter,
                image_512x512=subcat_1.image_512x512.url,
                image_640x275=subcat_1.image_640x275.url,
                image_1024x575=subcat_1.image_1024x575.url,
                image_1024x1024=subcat_1.image_1024x1024.url,
                image_1536x860=subcat_1.image_1536x860.url,
                image_2048x1150=subcat_1.image_2048x1150.url,
            ),
            list_images=BaseListImageRecord(
                image500x305=subcat_1.image500x305.url,
                image600x440=subcat_1.image600x440.url,
                image850x520=subcat_1.image850x520.url,
            ),
        )

        # Test category with parent, but not children.
        # Uses 1 query for getting category.
        with django_assert_max_num_queries(1):
            subcat_1_detail_record = category_detail_record(category=subcat_1)

        assert subcat_1_detail_record == expected_child_output
