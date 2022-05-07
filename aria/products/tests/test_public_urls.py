from django.urls import reverse


class TestPublicProductsUrls:
    def test_url_products_detail(self):
        """
        Test reverse match of ProductDetailAPI endpoint.
        """

        url = reverse("products-detail", args=["product_slug"])
        assert url == "/api/products/product/product_slug/"
