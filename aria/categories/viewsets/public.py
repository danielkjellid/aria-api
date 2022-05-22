from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from aria.categories.models import Category
from aria.core.deprecated_schemas import APIViewSchema
from aria.core.pagination import LimitOffsetPagination, get_paginated_response
from aria.core.serializers import BaseHeaderImageSerializer, inline_serializer
from aria.products.selectors import product_list_by_category


class CategoryProductsListAPI(APIView):
    """
    [PUBLIC] Endpoint for getting a list of products in
    a specific category.
    """

    permission_classes = (AllowAny,)
    authentication_classes = ()
    schema = APIViewSchema()

    class Pagination(LimitOffsetPagination):
        limit = 24

    class SearchSerializer(serializers.Serializer):
        search = serializers.CharField(required=False)

    class OutputSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        name = serializers.CharField()
        slug = serializers.SlugField()
        unit = serializers.CharField(source="get_unit_display")
        thumbnail = serializers.CharField(source="thumbnail.url")
        display_price = serializers.BooleanField(
            source="get_display_price"
        )  # TODO: not good, does more queries than needed
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
        variants = inline_serializer(
            source="get_variants",
            many=True,
            read_only=True,
            fields={
                "id": serializers.IntegerField(),
                "name": serializers.CharField(),
                "thumbnail": serializers.CharField(source="thumbnail.url"),
                "image": serializers.CharField(source="image.url"),
            },
        )

    @APIViewSchema.serializer(OutputSerializer())
    @APIViewSchema.query_parameters(SearchSerializer())
    def get(self, request: HttpRequest, category_slug: str) -> HttpResponse:
        category = get_object_or_404(Category, slug=category_slug)

        filters_serializer = self.SearchSerializer(data=request.query_params)
        filters_serializer.is_valid(raise_exception=True)

        products = product_list_by_category(
            category=category, filters=filters_serializer.validated_data
        )

        return get_paginated_response(
            pagination_class=self.Pagination,
            serializer_class=self.OutputSerializer,
            queryset=products,
            request=request,
            view=self,
        )


class CategoryDetailAPI(APIView):
    """
    [PUBLIC] Endpoint for getting a details of a specific
    category, parent or child.
    """

    permission_classes = (AllowAny,)
    authentication_classes = ()
    schema = APIViewSchema()

    class OutputSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        name = serializers.CharField()
        slug = serializers.SlugField()
        images = BaseHeaderImageSerializer(source="*", read_only=True)

    @APIViewSchema.serializer(OutputSerializer())
    def get(self, request: HttpRequest, category_slug: str) -> HttpResponse:
        category = get_object_or_404(Category, slug=category_slug)
        serializer = self.OutputSerializer(category)

        return Response(serializer.data, status=status.HTTP_200_OK)
