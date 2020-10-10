from django.urls import path
from users.api.viewsets import UsersListAPIView, UserDetailAPIView, UserCreateAPIView, RequestUserRetrieveAPIView

urlpatterns = [
    # endpoint for getting info about request user
    path('user/', RequestUserRetrieveAPIView.as_view(), name='request-user'),
    # endpoint for getting all users
    path('users/', UsersListAPIView.as_view(), name='users-list'),
    # endpoint for getting a single user instance
    path('users/<int:pk>/', UserDetailAPIView.as_view(), name='user-detail'),
    # endpoint for creating a single user instance
    path('users/create/', UserCreateAPIView.as_view(), name ='user-create'),
]