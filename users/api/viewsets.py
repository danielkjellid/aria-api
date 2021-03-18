from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.debug import sensitive_post_parameters
from rest_framework import filters, generics, permissions, status
from rest_framework.decorators import api_view
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.authentication import JWTAuthenticationSafe
from core.permissions import HasUserOrGroupPermission
from users.api.serializers import (PasswordResetConfirmSerializer,
                                   PasswordResetSerializer,
                                   RequestUserSerializer, UserCreateSerializer,
                                   UserNoteSerializer, UserSerializer,
                                   UsersSerializer)
from users.models import User
from utils.pagination import PageNumberSetPagination
from utils.models import AuditLog, Note
from utils.api.serializers import CreateNoteSerializer, UpdateNoteSerializer

sensitive_post_parameters_m = method_decorator(
    sensitive_post_parameters(
        'password', 'old_password', 'new_password1', 'new_password2'
    )
)

class UsersListCreateAPIView(generics.ListCreateAPIView):
    """
    View for listing all users in the application.

    Returns list of users.
    """

    queryset = User.objects.all().order_by('id')
    pagination_class = PageNumberSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ('first_name', 'last_name', 'email', 'phone_number')
    permission_classes = (IsAdminUser, HasUserOrGroupPermission)
    required_permissions = {
        'GET': ['has_users_list'],
        'POST': ['has_user_add'],
    }

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UsersSerializer
        
        return UserCreateSerializer


class UserDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    View for viewing, updating or deleting a single user instance

    Accepts the followinf POST/PUT parameters:
    - last_login
    - email
    - first_name
    - last_name
    - phone_number
    - has_confirmed_email
    - street_address
    - zip_code
    - zip_place
    - disabled_emails
    - subscribed_to_newsletter
    - allow_personalization
    - allow_third_party_personalization
    - date_joined
    - is_active

    Returns a single user instance
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminUser, HasUserOrGroupPermission)
    required_permissions = {
        'GET': ['has_users_list'],
        'PUT': ['has_user_edit'],
        'DELETE': ['has_user_delete']
    }

    def put(self, request, pk):
        user = get_object_or_404(User, pk = pk)
        serializer = UserSerializer(user, data=request.data)
        
        if serializer.is_valid():
            # store old user in variable
            old_user_instance = get_object_or_404(User, pk = pk)
            # update user instance
            serializer.save()
            # create logging instance by comparing old vs. new user fields
            AuditLog.create_log_entry(request.user, User, old_user_instance)
            
            # return updated user
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserNoteAPIView(APIView):

    queryset = Note.objects.all()
    permission_classes = (IsAdminUser, HasUserOrGroupPermission)
    required_permissions = {
        'GET': ['has_users_list'],
        'POST': ['has_notes_add'],
        'PUT': ['has_note_edit'],
    }

    def get_object(self, pk):
        user = get_object_or_404(User, pk=pk)
        return user

    def get(self, request, pk):
        user = self.get_object(pk)
        user_notes = Note.get_notes(user)
        serializer = UserNoteSerializer(user_notes, many=True)
        return Response(serializer.data)

    def post(self, request, pk):
        user = self.get_object(pk)
        serializer = CreateNoteSerializer(data=request.data)

        if serializer.is_valid():
            Note.create_note(request.user, user, serializer.data['note'])
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):

        serializer = UpdateNoteSerializer(data=request.data)

        if serializer.is_valid():
            Note.update_note(request.user, serializer.data['id'], serializer.data['note'])
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



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


class PasswordResetView(generics.GenericAPIView):
    """
    View for reseting password.

    Calls Django Auth PasswordResetForm save method.

    Accepts the following POST parameters: email
    Returns the success/fail message.
    """
    serializer_class = PasswordResetSerializer
    permission_classes = (AllowAny, )
    authentication_classes = ()

    def post(self, request, *args, **kwargs):
        """
        Create a serializer with request.data
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save()

        return Response(
            {'detail': _('Password reset e-mail has been sent.')},
            status=status.HTTP_200_OK
        )


class PasswordResetConfirmView(generics.GenericAPIView):
    """
    Password reset e-mail link is confirmed, therefore
    this resets the user's password.

    Accept the following POST parameters: token, uid, new_password1, 
    new_password2

    Returns the success/fail message.
    """
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = (AllowAny, )
    authentication_classes = ()

    @sensitive_post_parameters_m
    def dispatch(self, *args, **kwargs):
        return super(PasswordResetConfirmView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({'detail': _('Password has been reset with the new password')})
