from django.urls import reverse


class TestPublicProductsUrls:
    def test_url_product_list_by_category_api(self) -> None:
        """
        Test reverse match of product_list_by_category_api endpoint.
        """
        url = reverse("api-1.0.0:products-{category_slug}", args=["category_slug"])
        assert url == "/api/products/category/category_slug/"

    def test_url_product_detail_api(self) -> None:
        """
        Test reverse match of product_detail_api endpoint.
        """
        url = reverse(
            "api-1.0.0:products-product-{product_slug}", args=["product_slug"]
        )
        assert url == "/api/products/product/product_slug/"
