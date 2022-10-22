from django.urls import reverse


class TestProductAttributesInternalUrls:
    def test_url_color_list_internal_api(self) -> None:
        """
        Test reverse match of color_list_internal_api endpoint.
        """
        url = reverse("api-1.0.0:product attributes-colors")
        assert url == "/api/v1/internal/product-attributes/colors/"

    def test_url_shape_list_internal_api(self) -> None:
        """
        Test reverse match of shape_list_internal_api endpoint.
        """
        url = reverse("api-1.0.0:product attributes-shapes")
        assert url == "/api/v1/internal/product-attributes/shapes/"

    def test_url_variant_list_internal_api(self) -> None:
        """
        Test reverse match of variant_list_internal_api endpoint.
        """
        url = reverse("api-1.0.0:product attributes-variants")
        assert url == "/api/v1/internal/product-attributes/variants/"

    def test_url_variant_create_internal_api(self) -> None:
        """
        Test reverse match of variant_create_internal_api endpoint.
        """
        url = reverse("api-1.0.0:product attributes-variants-create")
        assert url == "/api/v1/internal/product-attributes/variants/create/"
