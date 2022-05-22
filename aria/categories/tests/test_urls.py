from django.urls import reverse


class TestPublicCategoriesUrls:
    def test_url_category_list_api(self):
        """
        Test reverse match of category_list_api endpoint.
        """
        url = reverse("api-1.0.0:categories-index")
        assert url == "/api/categories/"

    def test_url_category_parent_list_api(self):
        """
        Test reverse match of category_parent_list_api endpoint.
        """
        url = reverse("api-1.0.0:categories-parents")
        assert url == "/api/categories/parents/"

    def test_url_category_detail_api(self):
        """
        Test reverse match of category_detail_api endpoint.
        """
        url = reverse(
            "api-1.0.0:categories-category-{category_slug}", args=["category_slug"]
        )
        assert url == "/api/categories/category/category_slug/"

    def test_url_category_children_list_api(self):
        """
        Test reverse match of category_detail_api endpoint.
        """
        url = reverse(
            "api-1.0.0:categories-category-{category_slug}-children",
            args=["category_slug"],
        )
        assert url == "/api/categories/category/category_slug/children/"

    def test_url_category_products_list_api(self):
        """
        Test reverse match of category_detail_api endpoint.
        """
        url = reverse(
            "api-1.0.0:categories-category-{category_slug}-products",
            args=["category_slug"],
        )
        assert url == "/api/categories/category/category_slug/products/"
