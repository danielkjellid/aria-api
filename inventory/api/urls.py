from django.urls import path
from inventory.api.viewsets import CategoryListAPIView, CategoriesNavigationListAPIView

urlpatterns = [
    path('categories/', CategoryListAPIView.as_view(), name='categories-list'),
    path('categories/navigation/', CategoriesNavigationListAPIView.as_view(), name='categories-navigation-list'),
]