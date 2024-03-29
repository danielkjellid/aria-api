from django.urls import reverse


class TestPublicKitchensUrls:
    def test_url_kitchen_list_api(self) -> None:
        """
        Test reverse match of kitchen_list_api endpoint.
        """
        url = reverse("api-1.0.0:kitchens-index")
        assert url == "/api/v1/kitchens/"

    def test_url_kitchen_detail_api(self) -> None:
        """
        Test reverse match of kitchen_detail_api endpoint.
        """
        url = reverse("api-1.0.0:kitchens-{kitchen_slug}", args=["kitchen_slug"])
        assert url == "/api/v1/kitchens/kitchen_slug/"
