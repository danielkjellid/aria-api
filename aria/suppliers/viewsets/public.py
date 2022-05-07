from django.http import HttpRequest, HttpResponse
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from aria.suppliers.models import Supplier


class SupplierListAPI(APIView):
    """
    [PUBLIC] Endpoint for getting a list of active suppliers.
    """

    permission_classes = (AllowAny,)
    authentication_classes = ()

    class OutputSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        name = serializers.CharField()
        website_link = serializers.CharField()
        logo = serializers.CharField(source="image.url")

    def get(self, request: HttpRequest) -> HttpResponse:
        suppliers = Supplier.objects.filter(is_active=True)
        serializer = self.OutputSerializer(suppliers, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
