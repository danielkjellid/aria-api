from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import Permission, update_last_login
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.sites.models import Site
from rest_framework import serializers
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode as uid_decoder
from django.utils.encoding import force_text

from users.models import User
from utils.models import AuditLog, Note
from utils.api.serializers import AuditLogSerializer


class UserProfileSerializer(serializers.Serializer):
    full_name = serializers.SerializerMethodField()
    initial = serializers.SerializerMethodField()
    avatar_color = serializers.CharField()

    def get_full_name(self, instance):
        return instance.get_full_name()

    def get_initial(self, instance):
        return instance.get_initial()


class UserNoteSerializer(serializers.ModelSerializer):
    """
    A serializer to display notes associated with a specific user
    """

    profile = UserProfileSerializer(source='user')

    class Meta:
        model = Note
        fields = ('id', 'profile', 'note', 'updated_at')


class UsersSerializer(serializers.ModelSerializer):
    """
    A serializer to display all users registered in the app
    """

    profile = UserProfileSerializer(source='*')

    class Meta:
        model = User
        fields = ('id', 'profile', 'email', 'is_active', 'date_joined')


class UserSerializer(serializers.ModelSerializer):
    """
    A serializer to retrive a specific user instance
    """

    profile = UserProfileSerializer(source='*', read_only=True)
    address = serializers.SerializerMethodField()
    acquisition_source = serializers.SerializerMethodField()
    audit_logs = serializers.SerializerMethodField()
    notes = serializers.SerializerMethodField()


    def get_full_name(self, instance):
        return instance.get_full_name()

    def get_address(self, instance):
        return instance.get_address()

    def get_acquisition_source(self, instance):
        if not instance.acquisition_source:
            return 'N/A'
        
        return instance.acquisition_source

    def get_audit_logs(self, instance):
        audit_logs = AuditLog.get_logs(instance)
        return AuditLogSerializer(audit_logs, many=True, read_only=True).data

    def get_notes(self, instance):
        notes = Note.get_notes(instance)
        return UserNoteSerializer(notes, many=True, read_only=True).data

    class Meta:
        model = User
        exclude = ('password', 'groups', 'user_permissions', 'is_superuser', 'is_staff', 'avatar_color')
        

class RequestUserSerializer(serializers.ModelSerializer):
    """
    A serializer to retrieve the current user
    """

    full_name = serializers.SerializerMethodField()
    initial = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()
    group_permissions = serializers.SerializerMethodField()
    is_authenticated = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('full_name', 'avatar_color', 'initial', 'email', 'is_authenticated', 'permissions', 'group_permissions', 'is_staff', 'is_superuser')

    def get_full_name(self, user):
        if user.is_authenticated:
            return user.get_full_name()
        
        return None

    def get_initial(self, user):
        if user.is_authenticated:
            return user.get_initial()

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
        # add site property to data
        data['site'] = Site.objects.get(pk=settings.SITE_ID)

        email = data.get('email')
        password = data.get('password')
        password2 = data.get('password2')
        site = data.get('site')
        
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

        # check if site exists
        if not site:
            raise serializers.ValidationError (
                {'site': 'Error getting site, please contact an admin'}
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


class PasswordResetSerializer(serializers.Serializer):
    """
    Serializer for requesting a user reset e-mail
    """

    email = serializers.EmailField()
    password_reset_form_class = PasswordResetForm

    def get_email_options(self):
        """
        Override this method to change default email options
        """
        return {
            'html_email_template_name': 'email/password_reset_email.html'
        }

    def validate_email(self, value):
        """
        Validate email and create PasswordResetForm with the serializer
        """
        self.reset_form = self.password_reset_form_class(data=self.initial_data)

        if not self.reset_form.is_valid():
            raise serializers.ValidationError(self.reset_form.errors)

        return value

    
    def save(self):
        request = self.context.get('request')

        options = {
            'use_https': request.is_secure(),
            'from_email': getattr(settings, 'DEFAULT_FROM_EMAIL'),
            'request': request
        }

        options.update(self.get_email_options())
        self.reset_form.save(**options)


class PasswordResetConfirmSerializer(serializers.Serializer):
    new_password1 = serializers.CharField(max_length=128)
    new_password2 = serializers.CharField(max_length=128)
    uid = serializers.CharField()
    token = serializers.CharField()

    set_password_form_class = SetPasswordForm

    def custom_validation(self, attrs):
        pass

    def validate(self, attrs):

        try:
            uid = force_text(uid_decoder(attrs['uid']))
            self.user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError({'uid': ['Invalid value']})

        self.custom_validation(attrs)

        # Construct SetPasswordForm instance
        self.set_password_form = self.set_password_form_class(
            user=self.user, data=attrs
        )

        if not self.set_password_form.is_valid():
            raise serializers.ValidationError(self.set_password_form.errors)
        if not default_token_generator.check_token(self.user, attrs['token']):
            raise serializers.ValidationError({'token': ['Invalid value']})

        return attrs

    def save(self):
        return self.set_password_form.save()