from django.urls import path
from inventory.api.viewsets import CategoryListAPIView, CategoryAPIView, CategoriesNavigationListAPIView, ProductListByCategoryAPIView

urlpatterns = [
    path('categories/', CategoryListAPIView.as_view(), name='categories-list'),
    path('categories/category/<str:category>/', CategoryAPIView.as_view(), name='category'),
    path('categories/navigation/', CategoriesNavigationListAPIView.as_view(), name='categories-navigation-list'),
    path('products/<str:category>/', ProductListByCategoryAPIView.as_view(), name='product-category-list'),
]