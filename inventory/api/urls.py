from django.urls import path
from inventory.api.viewsets import CategoriesNavigationListAPIView

urlpatterns = [
    path('categories/navigation/', CategoriesNavigationListAPIView.as_view(), name='categories-navigation-list'),
]