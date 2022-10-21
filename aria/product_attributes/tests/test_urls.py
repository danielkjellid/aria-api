from django.urls import reverse


class TestProductAttributesInternalUrls:
    def test_url_shape_list_internal_api(self) -> None:
        """
        Test reverse match of shape_list_internal_api endpoint.
        """
        url = reverse("api-1.0.0:product attributes-shapes")
        assert url == "/api/v1/internal/product-attributes/shapes/"
