from dataclasses import dataclass
from django.forms import IntegerField
from django.http import HttpRequest, HttpResponse
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from aria.core.pagination import LimitOffsetPagination, get_paginated_response
from aria.core.exceptions import ApplicationError
from aria.core.serializers import inline_serializer
from aria.users.models import User

from aria.products.models import Product


class ProductListAPI(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = ()

    class Pagination(LimitOffsetPagination):
        limit = 24

    class FilterSerializer(serializers.Serializer):
        pass

    class OutputSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        name = serializers.CharField()
        unit = serializers.CharField(source="get_unit_display")
        thumbnail = serializers.CharField(source="thumbnail.url", read_only=True)
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
        variants = inline_serializer(
            source="get_variants",
            many=True,
            read_only=True,
            fields={
                "name": serializers.CharField(),
                "thumbnail": serializers.CharField(),
                "image": serializers.CharField(source="image.url"),
            },
        )
        materials = inline_serializer(
            source="get_materials_display",
            many=True,
            read_only=True,
            fields={"name": serializers.CharField()},
        )
        rooms = inline_serializer(
            source="get_rooms_display",
            many=True,
            read_only=True,
            fields={"name": serializers.CharField()},
        )
        supplier = serializers.StringRelatedField()

    def get(self, request: HttpRequest) -> HttpResponse:
        # Todo - add new selector
        data = Product.objects.filter(status=3)

        return get_paginated_response(
            pagination_class=self.Pagination,
            serializer_class=self.OutputSerializer,
            queryset=data,
            request=request,
            view=self,
        )
