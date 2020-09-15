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
                                       ProductFiltersByCategorySerializer,
                                       ProductListByCategorySerializer,
                                       SubCategoryFilterListSerializer)
from inventory.models import (Category, Product, ProductApplication,
                              ProductColor, ProductMaterial, ProductStyle,
                              SubCategory)


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
            status='available'
        ).distinct() #iexact to ignore upper/lowercase sensitivity and distinct to only return one object


class ProductFiltersListByCategory(generics.ListAPIView):
    """
    This viewset takes the category parameter from the url and returns related product filters
    """

    def get(self, request, *args, **kwargs):
        """
        Gets parameter in urls and aggregated filtered result
        """
        category = self.kwargs['category']

        categories = SubCategory.objects.filter(
            products__category__parent__name__iexact=category,
            is_active=True,
            products__status='available'
        ).values('name').annotate(
            count=Count('products', distinct=True)
        )

        colors = ProductColor.objects.filter(
            product_color__category__parent__name__iexact=category,
            product_color__status='available'
        ).values('name', 'color_hex').annotate(
            count=Count('product_color', distinct=True)
        )

        styles = ProductStyle.objects.filter(
            product_style__category__parent__name__iexact=category,
            product_style__status='available'
        ).values('name').annotate(
            count=Count('product_style', distinct=True)
        )

        applications = ProductApplication.objects.filter(
            product_application__category__parent__name__iexact=category,
            product_application__status='available'
        ).values('name').annotate(
            count=Count('product_application', distinct=True)
        )

        materials = ProductMaterial.objects.filter(
            product_material__category__parent__name__iexact=category,
            product_material__status='available'
        ).values('name').annotate(
            count=Count('product_material', distinct=True)
        )

        data = {'categories': categories, 'colors': colors, 'styles': styles, 'applications': applications, 'materials': materials}

        return Response(data)
