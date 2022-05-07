from django.urls import path

from aria.categories.viewsets.public import (
    CategoryChildrenListAPI,
    CategoryDetailAPI,
    CategoryListAPI,
    CategoryParentListAPI,
    CategoryProductsListAPI,
)

internal_patterns = []

public_patterns = [
    path(
        "",
        CategoryListAPI.as_view(),
        name="categories-list",
    ),
    path("parents/", CategoryParentListAPI.as_view(), name="categories-parents-list"),
    path(
        "category/<slug:category_slug>/", CategoryDetailAPI.as_view(), name="categories-detail"
    ),
    path(
        "category/<slug:category_slug>/children/",
        CategoryChildrenListAPI.as_view(),
        name="categories-parent-children-list",
    ),
    path(
        "category/<slug:category_slug>/products/",
        CategoryProductsListAPI.as_view(),
        name="category-products-list",
    ),
]

urlpatterns = internal_patterns + public_patterns
