from rest_framework import generics
from rest_framework.permissions import AllowAny

from aria.kitchens.models import Kitchen
from aria.kitchens.serializers import KitchenListSerializer, KitchenSerializer
from aria.products.enums import ProductStatus


class KitchenListAPIView(generics.ListAPIView):
    """
    Viewset for listing available kitchens
    """

    permission_classes = (AllowAny,)
    authentication_classes = ()
    serializer_class = KitchenListSerializer
    queryset = Kitchen.objects.filter(status=ProductStatus.AVAILABLE).order_by("id")


class KitchenRetrieveAPIView(generics.RetrieveAPIView):
    """
    Viewset for getting a specific kitchen instance based on slug
    """

    permission_classes = (AllowAny,)
    authentication_classes = ()
    serializer_class = KitchenSerializer
    lookup_field = "slug"
    queryset = Kitchen.objects.all()