from django.urls import reverse


class TestPublicDiscountsUrls:
    def test_url_discount_list_api(self) -> None:
        """
        Test reverse match of discount_list_api endpoint.
        """
        url = reverse("api-1.0.0:discounts-index")

        assert url == "/api/v1/discounts/"
