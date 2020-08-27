from rest_framework import generics, permissions
from rest_framework.generics import get_object_or_404

from core.permissions import HasUserOrGroupPermission
from inventory.api.serializers import CategorySerializer
from inventory.models import Category


class CategoriesNavigationListAPIView(generics.ListAPIView):
    queryset = Category.objects.filter(display_in_navbar=True, is_active=True).order_by('ordering')
    serializer_class = CategorySerializer