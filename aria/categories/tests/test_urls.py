from django.urls import reverse


class TestPublicCategoriesUrls:
    def test_url_category_list_api(self):
        """
        Test reverse match of category_list_api endpoint.
        """
        url = reverse("api-1.0.0:categories-index")
        assert url == "/api/ninja/categories/"
