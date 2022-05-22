from django.urls import path

from aria.categories.viewsets.public import CategoryDetailAPI, CategoryProductsListAPI

internal_patterns = []

public_patterns = [
    path(
        "category/<slug:category_slug>/",
        CategoryDetailAPI.as_view(),
        name="categories-detail",
    ),
    path(
        "category/<slug:category_slug>/products/",
        CategoryProductsListAPI.as_view(),
        name="category-products-list",
    ),
]

urlpatterns = internal_patterns + public_patterns
