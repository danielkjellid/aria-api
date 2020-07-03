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


class RequestUserSerializer(serializers.ModelSerializer):
    
    permissions = serializers.SerializerMethodField()
    group_permissions = serializers.SerializerMethodField()

    class Meta:
        model = User
        exclude = ('password', 'groups', 'user_permissions', )

    def get_permissions(self, instance):
        permissions = Permission.objects.filter(user=instance.id).values_list('codename', flat=True)
        return permissions

    def get_group_permissions(self, instance):
        permissions = Permission.objects.filter(group__user=instance.id).values_list('codename', flat=True)
        return permissions