from django.urls import reverse


class TestPublicCategoriesUrls:
    def test_url_category_list(self):
        """
        Test reverse match of CategoryListAPI endpoint.
        """

        url = reverse("categories-list")
        assert url == "/api/categories/"

    def test_url_category_detail(self):
        """
        Test reverse match of CategoryDetailAPI endpoint.
        """

        url = reverse("categories-detail", args=["category_slug"])
        assert url == "/api/categories/category_slug/"

    def test_url_category_parent_list(self):
        """
        Test reverse match of CategoryParentListAPI endpoint.
        """

        url = reverse("categories-parents-list")
        assert url == "/api/categories/parents/"

    def test_url_category_children_list(self):
        """
        Test reverse match of CategoryChildrenListAPI endpoint.
        """

        url = reverse("categories-parent-children-list", args=["category_slug"])
        assert url == "/api/categories/category_slug/children/"

    def test_url_category_products_list(self):
        """
        Test reverse match of CategoryProductsListAPI endpoint.
        """

        url = reverse("category-products-list", args=["category_slug"])
        assert url == "/api/categories/category_slug/products/"
