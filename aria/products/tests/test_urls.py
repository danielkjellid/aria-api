from django.urls import reverse


class TestPublicProductsUrls:
    def test_url_product_list_api(self) -> None:
        """
        Test reverse match of product_list_api endpoint.
        """
        url = reverse("api-1.0.0:products-index")
        assert url == "/api/v1/products/"

    def test_url_product_list_by_category_api(self) -> None:
        """
        Test reverse match of product_list_by_category_api endpoint.
        """
        url = reverse(
            "api-1.0.0:products-category-{category_slug}", args=["category_slug"]
        )
        assert url == "/api/v1/products/category/category_slug/"

    def test_url_product_detail_api(self) -> None:
        """
        Test reverse match of product_detail_api endpoint.
        """
        url = reverse("api-1.0.0:products-{product_slug}", args=["product_slug"])
        assert url == "/api/v1/products/product_slug/"


class TestInternalProductUrls:
    def test_url_product_list_internal_api(self) -> None:
        """
        Test reverse match of product_list_internal_api endpoint.
        """
        url = reverse("api-internal-1.0.0:products-index")
        assert url == "/api/v1/internal/products/"

    def test_url_product_create_internal_api(self) -> None:
        """
        Test reverse match of product_create_internal_api endpoint.
        """
        url = reverse("api-internal-1.0.0:products-create")
        assert url == "/api/v1/internal/products/create/"

    def test_url_product_image_create_internal_api(self) -> None:
        """
        Test reverse match of product_image_create_internal_api endpoint.
        """
        url = reverse(
            "api-internal-1.0.0:products-{product_id}-images-create",
            args=["product_id"],
        )
        assert url == "/api/v1/internal/products/product_id/images/create/"

    def test_url_product_file_create_internal_api(self) -> None:
        """
        Test reverse match of product_file_create_internal_api endpoint.
        """
        url = reverse(
            "api-internal-1.0.0:products-{product_id}-files-create", args=["product_id"]
        )
        assert url == "/api/v1/internal/products/product_id/files/create/"

    def test_url_product_option_create_internal_api(self) -> None:
        """
        Test reverse match of product_option_create_internal_api endpoint.
        """
        url = reverse(
            "api-internal-1.0.0:products-{product_id}-options-create",
            args=["product_id"],
        )
        assert url == "/api/v1/internal/products/product_id/options/create/"

    def test_url_product_option_bulk_create_internal_api(self) -> None:
        """
        Test reverse match of product_option_bulk_create_internal_api endpoint.
        """
        url = reverse(
            "api-internal-1.0.0:products-{product_id}-options-bulk-create",
            args=["product_id"],
        )
        assert url == "/api/v1/internal/products/product_id/options/bulk-create/"
