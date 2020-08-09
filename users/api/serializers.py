from django.contrib.auth.models import Permission 
from rest_framework import serializers
from users.models import User


class UsersSerializer(serializers.ModelSerializer):
    """
    A serializer to display all users registered in the app
    """

    full_name = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'full_name', 'email', 'address', 'date_joined', 'is_active')

    def get_full_name(self, instance):
        return instance.get_full_name()

    def get_address(self, instance):
        return instance.get_address()


class UserSerializer(serializers.ModelSerializer):
    """
    A serializer to retrive a specific user instance
    """

    full_name = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()
    acquisition_source = serializers.SerializerMethodField()


    def get_full_name(self, instance):
        return instance.get_full_name()

    def get_address(self, instance):
        return instance.get_address()

    def get_acquisition_source(self, instance):
        if not instance.acquisition_source:
            return 'Ingen'
        
        return instance.acquisition_source

    class Meta:
        model = User
        exclude = ('password', 'groups', 'user_permissions', 'is_superuser', 'is_staff')


class RequestUserSerializer(serializers.ModelSerializer):
    """
    A serializer to retrieve the current user
    """

    permissions = serializers.SerializerMethodField()
    group_permissions = serializers.SerializerMethodField()
    is_authenticated = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('is_authenticated', 'permissions', 'group_permissions', 'is_staff', 'is_superuser')

    def get_permissions(self, user):
        if not user.is_authenticated:
            return None

        permissions = Permission.objects.filter(user=user.id).values_list('codename', flat=True)
        return permissions

    def get_group_permissions(self, user):
        if not user.is_authenticated:
            return None

        group_permissions = Permission.objects.filter(group__user=user.id).values_list('codename', flat=True)
        return group_permissions
    
    def get_is_authenticated(self, user):
        return user.is_authenticated