from django.urls import path
from inventory.api.viewsets import (CategoriesNavigationListAPIView,
                                    CategoryAPIView, CategoryListAPIView,
                                    ProductListByCategoryAPIView,
                                    ProductRetrieveAPIView)

urlpatterns = [
    # endpoint for geting list of all categories
    path('categories/', CategoryListAPIView.as_view(), name='categories-list'),
    # endpoint for getting available categories used in the navbar
    path('categories/navigation/', CategoriesNavigationListAPIView.as_view(), name='categories-navigation-list'),
    # endpoint for getting a single category instance
    path('categories/<slug:category>/', CategoryAPIView.as_view(), name='category'),
    # endpoint for getting all products appended to a parent category
    path('categories/<slug:category>/products/', ProductListByCategoryAPIView.as_view(), name='category-product-list'),
    # endpoint for getting a single product instance
    path('categories/<slug:category>/products/<slug:slug>/', ProductRetrieveAPIView.as_view(), name='category-product')
]
