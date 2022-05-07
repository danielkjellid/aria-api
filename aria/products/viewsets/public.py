from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from aria.core.schemas import APIViewSchema
from aria.core.serializers import BaseHeaderImageSerializer, inline_serializer
from aria.products.models import Product


class ProductDetailAPI(APIView):
    """
    [PUBLIC] Endpoint for retrieving a specific product. Takes the
    product slug as a parameter.
    """

    permission_classes = (AllowAny,)
    authentication_classes = ()
    schema = APIViewSchema()

    class OutputSerializer(serializers.Serializer):
        # Product meta
        id = serializers.IntegerField()
        status = serializers.CharField(source="get_status_display")
        unit = serializers.CharField(source="get_unit_display")
        name = serializers.CharField()
        description = serializers.CharField(
            source="new_description"
        )  # TODO: remove source when migrated to new_desc
        images = BaseHeaderImageSerializer(read_only=True, many=True)

        # Specification fields
        absorption = serializers.CharField()
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
        origin_country = serializers.StringRelatedField(
            source="supplier.origin_country", read_only=True
        )

        # Product details
        available_in_special_sizes = serializers.BooleanField()
        options = inline_serializer(
            many=True,
            read_only=True,
            fields={
                "id": serializers.IntegerField(),
                "variant": inline_serializer(
                    fields={
                        "id": serializers.IntegerField(),
                        "name": serializers.CharField(),
                        "thumbnail": serializers.CharField(source="thumbnail.url"),
                        "image": serializers.CharField(source="image.url"),
                    }
                ),
                "size": inline_serializer(
                    fields={
                        "id": serializers.IntegerField(),
                        "name": serializers.StringRelatedField(source="*"),
                    }
                ),
            },
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
        files = inline_serializer(
            many=True,
            read_only=True,
            fields={
                "name": serializers.CharField(),
                "file": serializers.CharField(source="file.url"),
            },
        )

    @APIViewSchema.serializer(OutputSerializer())
    def get(self, request: HttpRequest, product_slug: str) -> HttpResponse:
        product = get_object_or_404(Product, slug=product_slug)
        serializer = self.OutputSerializer(product)

        return Response(serializer.data, status=status.HTTP_200_OK)
