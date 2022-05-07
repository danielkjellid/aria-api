from rest_framework import generics
from rest_framework.permissions import AllowAny

from aria.product_categorization.models import Category, SubCategory
from aria.product_categorization.serializers import (
    CategoryListSerializer,
    CategoryNavigationListSerializer,
    CategorySerializer,
    SubCategoryListSerializer,
)


class CategoriesNavigationListAPIView(generics.ListAPIView):
    """
    Vierset for listing categories and subcategories to be listed in the navbar
    """

    permission_classes = (AllowAny,)
    authentication_classes = ()
    queryset = Category.on_site.filter(display_in_navbar=True, is_active=True).order_by(
        "ordering"
    )
    serializer_class = CategoryNavigationListSerializer


class CategoryListAPIView(generics.ListAPIView):
    """
    Viewset for listing all categories and its associated images, does not include children
    """

    permission_classes = (AllowAny,)
    authentication_classes = ()
    queryset = Category.on_site.filter(is_active=True).order_by("ordering")
    serializer_class = CategoryListSerializer


class CategoryRetrieveAPIView(generics.RetrieveAPIView):
    """
    Viewset for listing a specific category instance
    """

    permission_classes = (AllowAny,)
    authentication_classes = ()
    serializer_class = CategorySerializer
    lookup_field = "slug"
    queryset = Category.on_site.filter(is_active=True)


class SubCategoryListAPIView(generics.ListAPIView):
    """
    Viewset for listing all subcategories and its associated images.
    """

    permission_classes = (AllowAny,)
    authentication_classes = ()
    serializer_class = SubCategoryListSerializer

    def get_queryset(self):
        category = self.kwargs["slug"]

        return SubCategory.on_site.filter(
            parent__slug=category, is_active=True
        ).order_by("ordering")


class SubCategoryRetrieveAPIView(generics.RetrieveAPIView):
    """
    Viewset for listing a specific category instance
    """

    permission_classes = (AllowAny,)
    authentication_classes = ()
    serializer_class = CategorySerializer
    lookup_field = "slug"
    queryset = SubCategory.on_site.filter(is_active=True)
