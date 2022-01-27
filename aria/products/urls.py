from django.urls import path

from aria.products.viewsets.public import ProductDetailAPI

internal_patterns = []

public_patterns = [
    path("<slug:product_slug>/", ProductDetailAPI.as_view(), name="product-detail"),
]

urlpatterns = internal_patterns + public_patterns
