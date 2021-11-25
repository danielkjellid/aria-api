from django.urls import path

from aria.product_categorization.viewsets import (
    CategoriesNavigationListAPIView,
    CategoryListAPIView,
    CategoryRetrieveAPIView,
)
from aria.products.viewsets import ProductListByCategoryAPIView

urlpatterns = [
    # endpoint for geting list of all categories
    path("categories/", CategoryListAPIView.as_view(), name="categories-list"),
    # endpoint for getting available categories used in the navbar
    path(
        "categories/navigation/",
        CategoriesNavigationListAPIView.as_view(),
        name="categories-navigation-list",
    ),
    # endpoint for getting a single category instance
    path("categories/<slug:slug>/", CategoryRetrieveAPIView.as_view(), name="category"),
    # endpoint for getting all products appended to a parent category
    path(
        "categories/<slug:category>/products/",
        ProductListByCategoryAPIView.as_view(),
        name="category-product-list",
    ),
]
