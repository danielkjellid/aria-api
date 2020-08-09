from django.urls import path
from users.api.viewsets import UsersListAPIView, UserDetailAPIView, RequestUserRetrieveAPIView

urlpatterns = [
    # generic users routes
    path('users/', UsersListAPIView.as_view(), name='users-list'),
    path('users/<int:pk>/', UserDetailAPIView.as_view(), name='user-detail'),

    # request user routes
    path('user/', RequestUserRetrieveAPIView.as_view(), name='request-user'),
]