from django.urls import reverse


class TestPublicCategoriesUrls:
    def test_url_category_list_api(self) -> None:
        """
        Test reverse match of category_list_api endpoint.
        """
        url = reverse("api-1.0.0:categories-index")
        assert url == "/api/v1/categories/"

    def test_url_category_parent_list_api(self) -> None:
        """
        Test reverse match of category_parent_list_api endpoint.
        """
        url = reverse("api-1.0.0:categories-parents")
        assert url == "/api/v1/categories/parents/"

    def test_url_category_detail_api(self) -> None:
        """
        Test reverse match of category_detail_api endpoint.
        """
        url = reverse(
            "api-1.0.0:categories-{category_slug}",
            args=["category_slug"],
        )
        assert url == "/api/v1/categories/category_slug/"

    def test_url_category_children_list_api(self) -> None:
        """
        Test reverse match of category_detail_api endpoint.
        """
        url = reverse(
            "api-1.0.0:categories-{category_slug}-children",
            args=["category_slug"],
        )
        assert url == "/api/v1/categories/category_slug/children/"


class TestInternalCategoriesUrls:
    def test_url_category_list_internal_api(self) -> None:
        """
        Test reverse match of category_list_internal_api endpoint.
        """
        url = reverse("api-1.0.0:internal-categories-index")
        assert url == "/api/v1/internal/categories/"
