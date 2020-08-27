from rest_framework import generics, permissions
from rest_framework.generics import get_object_or_404

from core.permissions import HasUserOrGroupPermission
from inventory.api.serializers import CategorySerializer
from inventory.models import Category


class CategoriesNavigationListAPIView(generics.ListAPIView):
    queryset = Category.objects.all().order_by('id')
    serializer_class = CategorySerializer