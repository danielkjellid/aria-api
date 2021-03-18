from django.urls import path
from inventory.api.viewsets import (CategoriesNavigationListAPIView,
                                    CategoryRetrieveAPIView, CategoryListAPIView,
                                    ProductListByCategoryAPIView,
                                    ProductRetrieveAPIView, KitchenListAPIView, KitchenRetrieveAPIView, ProductListCreateAPIView)

urlpatterns = [
    # endpoint for geting list of all categories
    path('categories/', CategoryListAPIView.as_view(), name='categories-list'),
    # endpoint for getting available categories used in the navbar
    path('categories/navigation/', CategoriesNavigationListAPIView.as_view(), name='categories-navigation-list'),
    # endpoint for getting a single category instance
    path('categories/<slug:slug>/', CategoryRetrieveAPIView.as_view(), name='category'),
    # endpoint for getting all products appended to a parent category
    path('categories/<slug:category>/products/', ProductListByCategoryAPIView.as_view(), name='category-product-list'),
    path('products/', ProductListCreateAPIView.as_view(), name='products-list'),
    # endpoint for getting a single product instance
    path('products/<slug:slug>/', ProductRetrieveAPIView.as_view(), name='product-detail'),
    # endpoint for geting list of all kitchens
    path('kitchens/', KitchenListAPIView.as_view(), name='kitchen_list'),
    # endpoint for getting a single kitchen instance
    path('kitchens/<slug:slug>/', KitchenRetrieveAPIView.as_view(), name='kitchen_detail'),
]
