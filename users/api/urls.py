from django.urls import path, re_path
from users.api.viewsets import UsersListAPIView, UserDetailAPIView, UserCreateAPIView, RequestUserRetrieveAPIView, PasswordResetView, PasswordResetConfirmView

urlpatterns = [
    # endpoint for getting info about request user
    path('user/', RequestUserRetrieveAPIView.as_view(), name='request-user'),
    # endpoint for getting all users
    path('users/', UsersListAPIView.as_view(), name='users-list'),
    # endpoint for getting a single user instance
    path('users/<int:pk>/', UserDetailAPIView.as_view(), name='user-detail'),
    # endpoint for creating a single user instance
    path('users/create/', UserCreateAPIView.as_view(), name ='user-create'),
    path('users/password/reset/', PasswordResetView.as_view(), name='reset-password'),
    #path('users/password/reset/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm')
    re_path(
        r'^users/password/reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', 
        PasswordResetConfirmView.as_view(),
        name='password_reset_confirm'
    ),
]