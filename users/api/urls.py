from django.urls import path
from users.api.viewsets import UsersListAPIView, RequestUserAPIView

urlpatterns = [
    path('user/', RequestUserAPIView.as_view(), name='request-user'),
    path('users/', UsersListAPIView.as_view(), name='users-list'),
]