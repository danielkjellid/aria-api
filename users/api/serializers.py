from django.contrib.auth import authenticate
from django.contrib.auth.models import Permission, update_last_login
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

    full_name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()
    group_permissions = serializers.SerializerMethodField()
    is_authenticated = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('full_name', 'email', 'is_authenticated', 'permissions', 'group_permissions', 'is_staff', 'is_superuser')

    def get_full_name(self, user):
        if user.is_authenticated:
            return user.get_full_name()
        
        return None

    def get_email(self, user):
        if user.is_authenticated:
            return user.email

        return None
    
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


class UserCreateSerializer(serializers.ModelSerializer):
    """
    A serializer for creating a user instance
    """

    password = serializers.CharField(min_length=8, write_only=True, required=True, style={'input_type': 'password'})
    password2 = serializers.CharField(min_length=8, write_only=True, style={'input_type': 'password'}, label='Confirm password')

    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'phone_number',
            'email',
            'password',
            'password2',
            'street_address',
            'zip_code',
            'zip_place',
            'subscribed_to_newsletter',
            'allow_personalization',
            'allow_third_party_personalization'
        )
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        password2 = data.get('password2')
        
        # check if passwords are equal
        if password != password2:
            raise serializers.ValidationError (
                {'password': 'The two passwords must be equal.'}
            )

        # check if email is unique
        if (email and User.objects.filter(email=email).exists()):
            raise serializers.ValidationError (
                {'email': 'Email address must be unique.'}
            )

        return data

    def create(self, validated_data):
        # remove password and password 2 from data
        password = validated_data.pop('password', None)
        password2 = validated_data.pop('password2', None)

        # create a new model instance
        instance = self.Meta.model(**validated_data)

        # set password
        if password is not None:
            instance.set_password(password)

        instance.save()

        return instance
