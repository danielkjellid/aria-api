from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from aria.categories.models import Category
from aria.categories.selectors import (
    categories_children_active_list,
    categories_navigation_active_list,
    categories_parent_active_list,
)
from aria.core.serializers import (
    BaseHeaderImageSerializer,
    BaseListImageSerializer,
    inline_serializer,
)


class CategoryListAPI(APIView):
    """
    [PUBLIC] Endpoint to fetch categories used for
    routing in the frontend navbar.
    """

    permission_classes = (AllowAny,)
    authentication_classes = ()

    class OutputSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        name = serializers.CharField()
        slug = serializers.SlugField()
        children = serializers.SerializerMethodField()

        class ChildSerializer(serializers.Serializer):
            id = serializers.IntegerField()
            name = serializers.CharField()
            slug = serializers.SlugField()
            ordering = serializers.IntegerField()

        def get_children(self, parent):

            children = categories_children_active_list(parent=parent)

            return self.ChildSerializer(children, many=True).data

    def get(self, request: HttpRequest) -> HttpResponse:
        categories = categories_navigation_active_list()
        serializer = self.OutputSerializer(categories, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class CategoryParentListAPI(APIView):
    """
    [PUBLIC] Endpoint for getting a list of parent
    categories.
    """

    permission_classes = (AllowAny,)
    authentication_classes = ()

    class OutputSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        name = serializers.CharField()
        slug = serializers.SlugField()
        ordering = serializers.IntegerField()
        images = BaseHeaderImageSerializer(source="*", read_only=True)

    def get(self, request: HttpRequest) -> HttpResponse:
        parent_categories = categories_parent_active_list()
        serializer = self.OutputSerializer(parent_categories, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class CategoryChildrenListAPI(APIView):
    """
    [PUBLIC] Endpoint for getting a list of children
    categories attached to a specific parent.
    """

    permission_classes = (AllowAny,)
    authentication_classes = ()

    class OutputSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        name = serializers.CharField()
        slug = serializers.SlugField()
        ordering = serializers.IntegerField()
        description = serializers.CharField()
        images = BaseListImageSerializer(source="*", read_only=True)

    def get(self, request: HttpRequest, category_slug: str) -> HttpResponse:
        parent = get_object_or_404(Category, slug=category_slug)
        children_categories = categories_children_active_list(parent=parent)
        serializer = self.OutputSerializer(children_categories, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class CategoryProductsListAPI(APIView):
    """
    [PUBLIC] Endpoint for getting a list of products in
    a specific category.
    """

    permission_classes = (AllowAny,)
    authentication_classes = ()

    class OutputSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        name = serializers.CharField()
        slug = serializers.SlugField()
        unit = serializers.CharField(source="get_unit_display")
        thumbnail = serializers.CharField(source="thumbnail.url")
        display_price = serializers.BooleanField()
        from_price = serializers.DecimalField(
            source="get_lowest_option_price",
            decimal_places=2,
            coerce_to_string=True,
            max_digits=8,
        )
        colors = inline_serializer(
            many=True,
            read_only=True,
            fields={
                "id": serializers.IntegerField(),
                "name": serializers.CharField(),
                "color_hex": serializers.CharField(),
            },
        )
        shapes = inline_serializer(
            many=True,
            read_only=True,
            fields={
                "name": serializers.CharField(),
                "image": serializers.CharField(source="image.url"),
            },
        )
        materials = inline_serializer(
            source="get_materials_display",
            many=True,
            read_only=True,
            fields={"name": serializers.CharField()},
        )
        variants = inline_serializer(  # TODO: add propper source when ready
            many=True,
            read_only=True,
            fields={
                "id": serializers.IntegerField(),
                "name": serializers.CharField(),
                "thumbnail": serializers.CharField(source="thumbnail.url"),
                "image": serializers.CharField(source="image.url"),
            },
        )

    def get(self, request: HttpRequest, category_slug: str) -> HttpResponse:
        category = get_object_or_404(Category, slug=category_slug)
        products = category.get_products()
        serializer = self.OutputSerializer(products, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class CategoryDetailAPI(APIView):
    """
    [PUBLIC] Endpoint for getting a details of a specific
    category, parent or child.
    """

    permission_classes = (AllowAny,)
    authentication_classes = ()

    class OutputSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        name = serializers.CharField()

    def get(self, request: HttpRequest, category_slug: str) -> HttpResponse:
        category = get_object_or_404(Category, slug=category_slug)
        serializer = self.OutputSerializer(category)

        return Response(serializer.data, status=status.HTTP_200_OK)
