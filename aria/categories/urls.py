from django.urls import path

from aria.categories.viewsets.public import (
    CategoryChildrenListAPI,
    CategoryDetailAPI,
    CategoryListAPI,
    CategoryParentListAPI,
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
        "<slug:category_slug>/", CategoryDetailAPI.as_view(), name="categories-detail"
    ),
    path(
        "<slug:category_slug>/children/",
        CategoryChildrenListAPI.as_view(),
        name="categories-parent-children-list",
    ),
]

urlpatterns = internal_patterns + public_patterns
