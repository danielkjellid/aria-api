from django.urls import path
from users.api.viewsets import UsersListAPIView, UserDetailAPIView, RequestUserPermissionsRetrieveAPIView

urlpatterns = [
    path('users/', UsersListAPIView.as_view(), name='users-list'),
    path('users/<int:pk>/', UserDetailAPIView.as_view(), name='user-detail'),
    path('user/permissions/', RequestUserPermissionsRetrieveAPIView.as_view(), name='request-user-permissions'),
]