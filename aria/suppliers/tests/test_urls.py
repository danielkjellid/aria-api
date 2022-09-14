from django.urls import reverse


class TestPublicSuppliersUrls:
    def test_url_supplier_list_api(self) -> None:
        """
        Test reverse match of supplier_list_api endpoint.
        """
        url = reverse("api-1.0.0:suppliers-index")
        assert url == "/api/v1/suppliers/"
