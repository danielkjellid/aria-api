from rest_framework import generics, permissions
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.permissions import HasUserOrGroupPermission
from users.api.serializers import RequestUserSerializer, UsersSerializer
from users.models import User


class RequestUserAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = RequestUserSerializer(request.user)
        return Response(serializer.data)

class UsersListAPIView(generics.ListCreateAPIView):
    queryset = User.objects.all().order_by('id')
    serializer_class = UsersSerializer
    permission_classes = [HasUserOrGroupPermission]
    required_permissions = {
        'GET': ['has_users_list']
    }
