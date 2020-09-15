from django.urls import path
from inventory.api.viewsets import CategoryListAPIView, CategoriesNavigationListAPIView, ProductListByCategoryAPIView, ProductFiltersListByCategory

urlpatterns = [
    path('categories/', CategoryListAPIView.as_view(), name='categories-list'),
    path('categories/navigation/', CategoriesNavigationListAPIView.as_view(), name='categories-navigation-list'),
    path('products/<str:category>/', ProductListByCategoryAPIView.as_view(), name='product-category-list'),
    path('products/<str:category>/filters/', ProductFiltersListByCategory.as_view(), name='product-filters-category-list'),
]