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
        assert False

    def test_url_product_create_internal_api(self) -> None:
        assert False

    def test_url_product_file_create_internal_api(self) -> None:
        assert False

    def test_url_variant_list_internal_api(self) -> None:
        assert False

    def test_url_variant_list_internal_api(self) -> None:
        assert False

    def test_url_variant_create_internal_api(self) -> None:
        assert False

    def test_url_product_option_create_internal_api(self) -> None:
        assert False

    def test_url_product_option_bulk_create_internal_api(self) -> None:
        assert False

    def test_url_color_list_internal_api(self) -> None:
        assert False

    def test_url_shape_list_internal_api(self) -> None:
        assert False
