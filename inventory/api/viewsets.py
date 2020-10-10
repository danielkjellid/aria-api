import json

from rest_framework import filters, generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from core.permissions import HasUserOrGroupPermission
from inventory.api.serializers import (CategoryListSerializer,
                                       CategoryNavigationListSerializer,
                                       CategorySerializer,
                                       ProductListByCategorySerializer,
                                       ProductSerializer)
from inventory.models import Category, Product


class CategoriesNavigationListAPIView(generics.ListAPIView):
    """
    Vierset for listing categories and subcategories to be listed in the navbar
    """
    permission_classes = (AllowAny, )
    authentication_classes = ()
    queryset = Category.objects.filter(display_in_navbar=True, is_active=True).order_by('ordering')
    serializer_class = CategoryNavigationListSerializer


class CategoryListAPIView(generics.ListAPIView):
    """
    Viewset for listing all categories and its associated images, does not include children
    """
    permission_classes = (AllowAny, )
    authentication_classes = ()
    queryset = Category.objects.filter(is_active=True).order_by('ordering')
    serializer_class = CategoryListSerializer


class CategoryAPIView(generics.ListAPIView):
    """
    Viewset for listing a specific category instance
    """
    permission_classes = (AllowAny, )
    authentication_classes = ()
    serializer_class = CategorySerializer

    def get_queryset(self):
        category = self.kwargs['category']
        return Category.objects.filter(slug=category, is_active=True)



class ProductListByCategoryAPIView(generics.ListAPIView):
    """
    This viewset takes the category parameter given by the url and find related products
    """
    permission_classes = (AllowAny, )
    authentication_classes = ()
    serializer_class = ProductListByCategorySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ('name', 'short_description', 'styles__name', 'materials__name')

    def get_queryset(self):
        """
        Gets parameter in urls and filters the product model
        """

        category = self.kwargs['category']
        return Product.objects.filter(
            category__parent__slug=category, 
            status=3
        ).distinct()


class ProductRetrieveAPIView(generics.RetrieveAPIView):
    permission_classes = (AllowAny, )
    authentication_classes = ()
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    lookup_field = 'slug'

    def get_queryset(self):
        category = self.kwargs['category']
        return Product.objects.filter(
            category__parent__slug=category, 
            status=3
        ).distinct()

