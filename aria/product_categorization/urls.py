from django.urls import path

from aria.product_categorization.viewsets import (
    CategoriesNavigationListAPIView,
    CategoryListAPIView,
    CategoryRetrieveAPIView,
    SubCategoryListAPIView,
    SubCategoryRetrieveAPIView,
)
# from aria.products.viewsets import (
#     ProductListBySubCategoryAPIView,
# )

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
        "categories/<slug:slug>/subcategories/",
        SubCategoryListAPIView.as_view(),
        name="category-subcategories",
    ),
    path(
        "categories/subcategory/<slug:slug>/",
        SubCategoryRetrieveAPIView.as_view(),
        name="subcategory",
    ),
    # path(
    #     "categories/<slug:subcategory>/products/",
    #     ProductListBySubCategoryAPIView.as_view(),
    #     name="product-subcategory-list",
    # ),
]
