from rest_framework import generics
from rest_framework.generics import get_object_or_404
from rest_framework import permissions

from users.models import User
from users.api.serializers import UsersSerializer
from core.permissions import HasUserOrGroupPermission


class UsersListAPIView(generics.ListCreateAPIView):
    queryset = User.objects.all().order_by('id')
    serializer_class = UsersSerializer
    permission_classes = [HasUserOrGroupPermission]
    required_permissions = {
        'GET': ['has_users_list']
    }