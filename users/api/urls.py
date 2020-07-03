from django.urls import path
from users.api.viewsets import UsersListAPIView

urlpatterns = [
    path('users/', UsersListAPIView.as_view(), name='users-list')
]