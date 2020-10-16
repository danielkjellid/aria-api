from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from core.permissions import HasUserOrGroupPermission
from core.authentication import JWTAuthenticationSafe
from users.api.serializers import (RequestUserSerializer, UserCreateSerializer,
                                   UserSerializer, UsersSerializer)
from users.models import User


class UsersListAPIView(generics.ListAPIView):
    """
    View for listing all users in the application
    """

    queryset = User.objects.all().order_by('id')
    serializer_class = UsersSerializer
    permission_classes = (IsAdminUser, HasUserOrGroupPermission)
    required_permissions = {
        'GET': ['has_users_list']
    }


class UserDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    View for viewing a single user instance
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminUser, HasUserOrGroupPermission)
    required_permissions = {
        'GET': ['has_users_list']
    }


class RequestUserRetrieveAPIView(generics.RetrieveAPIView):
    """
    View for getting info about request user
    """
    permission_classes = (IsAuthenticated, )
    authentication_classes = (JWTAuthenticationSafe, )

    def get(self, request):
        serializer = RequestUserSerializer(request.user)
        return Response(serializer.data)


class UserCreateAPIView(generics.CreateAPIView):
    """
    View for creating a user instance
    """

    # set view public
    permission_classes = (AllowAny, )
    authentication_classes = ()

    # use the UserCreate serializer
    serializer_class = UserCreateSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            if user:
                json = serializer.data
                return Response(json, status=status.HTTP_201_CREATED)
                
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
