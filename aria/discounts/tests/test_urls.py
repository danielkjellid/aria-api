from django.urls import reverse


class TestPublicDiscountsUrls:
    def test_url_discount_active_list_api(self) -> None:
        """
        Test reverse match of discount_active_list_api endpoint.
        """
        url = reverse("api-1.0.0:discounts-active")

        assert url == "/api/discounts/active/"
