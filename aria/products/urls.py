from django.urls import path

from aria.products.views import ProductListCreateAPIView
from aria.products.viewsets.public import ProductDetailAPI

internal_patterns = []

public_patterns = [
    path("<slug:product_slug>/", ProductDetailAPI.as_view(), name="detail"),
    # endpoint for getting all products
    path("products/", ProductListCreateAPIView.as_view(), name="products-list"),
]

urlpatterns = internal_patterns + public_patterns
