from django.urls import path
from users.api.viewsets import UsersListAPIView, RequestUserPermissionsRetrieveAPIView

urlpatterns = [
    path('user/permissions/', RequestUserPermissionsRetrieveAPIView.as_view(), name='user-permissions'),
    path('users/', UsersListAPIView.as_view(), name='users-list'),
]