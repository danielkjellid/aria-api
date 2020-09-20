import json

from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from core.permissions import HasUserOrGroupPermission
from inventory.api.serializers import (CategoryListSerializer,
                                       CategoryNavigationListSerializer,
                                       ProductListByCategorySerializer)
from inventory.models import (Category, Product)


class CategoriesNavigationListAPIView(generics.ListAPIView):
    """
    Vierset for listing categories and subcategories to be listed in the navbar
    """

    queryset = Category.objects.filter(display_in_navbar=True, is_active=True).order_by('ordering')
    serializer_class = CategoryNavigationListSerializer


class CategoryListAPIView(generics.ListAPIView):
    """
    Viewset for listing all categories and its associated images, does not include children
    """

    queryset = Category.objects.filter(is_active=True).order_by('ordering')
    serializer_class = CategoryListSerializer


class ProductListByCategoryAPIView(generics.ListAPIView):
    """
    This viewset takes the category parameter given by the url and find related products
    """

    serializer_class = ProductListByCategorySerializer

    def get_queryset(self):
        """
        Gets parameter in urls and filters the product model
        """

        category = self.kwargs['category']
        return Product.objects.filter(
            category__parent__name__iexact=category, 
            status=3
        ).distinct() #iexact to ignore upper/lowercase sensitivity and distinct to only return one object
