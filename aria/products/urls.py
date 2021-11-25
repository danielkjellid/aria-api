from django.urls import path

from aria.products.viewsets import (
    ProductListByCategoryAPIView,
    ProductListCreateAPIView,
    ProductRetrieveAPIView,
)

urlpatterns = [
    # endpoint for getting all products
    path("products/", ProductListCreateAPIView.as_view(), name="products-list"),
    # endpoint for getting a single product instance
    path(
        "products/<slug:slug>/", ProductRetrieveAPIView.as_view(), name="product-detail"
    ),
]
