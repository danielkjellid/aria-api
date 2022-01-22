from django.conf import settings
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.forms import CharField
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text
from django.utils.http import (
    urlsafe_base64_decode as uid_decoder,
    urlsafe_base64_encode as uid_encoder,
)
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from aria.audit_logs.models import LogEntry
from aria.audit_logs.serializers import LogEntrySerializer
from aria.core.serializers import inline_serializer
from aria.notes.models import NoteEntry
from aria.users.models import User
from aria.users.selectors import get_user_group_permissions, get_user_permissions


class RequestUserSerializer(serializers.ModelSerializer):
    """
    A serializer to retrieve the current user
    """

    full_name = serializers.CharField()
    initial = serializers.CharField()
    email = serializers.CharField()
    permissions = serializers.SerializerMethodField()
    group_permissions = serializers.SerializerMethodField()
    is_authenticated = serializers.BooleanField()

    class Meta:
        model = User
        fields = (
            "first_name",
            "full_name",
            "avatar_color",
            "initial",
            "email",
            "is_authenticated",
            "permissions",
            "group_permissions",
            "is_staff",
            "is_superuser",
            "has_confirmed_email",
        )

    def get_permissions(self, user):
        return get_user_permissions(user=user)

    def get_group_permissions(self, user):
        return get_user_group_permissions(user=user)


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
        return {"html_email_template_name": "email/password_reset_email.html"}

    def validate_email(self, value):
        """
        Validate email and create PasswordResetForm with the serializer
        """
        self.reset_form = self.password_reset_form_class(data=self.initial_data)

        if not self.reset_form.is_valid():
            raise serializers.ValidationError(self.reset_form.errors)

        return value

    def save(self):
        request = self.context.get("request")

        options = {
            "use_https": request.is_secure(),
            "from_email": getattr(settings, "DEFAULT_FROM_EMAIL"),
            "request": request,
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
            uid = force_text(uid_decoder(attrs["uid"]))
            self.user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError({"uid": ["Invalid value"]})

        self.custom_validation(attrs)

        # Construct SetPasswordForm instance
        self.set_password_form = self.set_password_form_class(
            user=self.user, data=attrs
        )

        if not self.set_password_form.is_valid():
            raise serializers.ValidationError(self.set_password_form.errors)
        if not default_token_generator.check_token(self.user, attrs["token"]):
            raise serializers.ValidationError({"token": ["Invalid value"]})

        return attrs

    def save(self):
        return self.set_password_form.save()


class AccountVerificationSerializer(serializers.Serializer):

    email = serializers.EmailField()

    def validate_email(self, value):
        """
        Check if email exits on site, and that the user,
        and that the user in question is active
        """
        try:
            self.user = User.objects.get(email__iexact=value)
            if self.user.is_active:
                return value
        except User.DoesNotExist:
            raise serializers.ValidationError({"detail": _("User does not exist")})

    def validate(self, data):
        """
        Check if email isn't already confirmed
        """
        if self.user.has_confirmed_email:
            raise serializers.ValidationError(
                {
                    "detail": _(
                        "Email is already confirmed, unable to resend verification email"
                    )
                }
            )

        return data

    def save(self):
        # constructor for verification email
        # sends uid and token in email
        user_verification_email = render_to_string(
            "email/verify_account.html",
            {
                "protocol": "https",
                "domain": "https://flis.no",
                "user": self.user,
                "uid": uid_encoder(force_bytes(self.user.pk)),
                "token": default_token_generator.make_token(self.user),
            },
        )

        # use email_user method and send verification email
        self.user.email_user(
            "Bekreft kontoen din på Flishuset",
            html_message=user_verification_email,
        )


class AccountVerificationConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()

    def validate(self, attrs):

        try:
            uid = force_text(uid_decoder(attrs["uid"]))
            self.user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError({"uid": ["Invalid value"]})

        if not default_token_generator.check_token(self.user, attrs["token"]):
            raise serializers.ValidationError({"token": ["Invalid value"]})

        if self.user.has_confirmed_email:
            raise serializers.ValidationError(
                {"detail": _("Konto er allerede verifisert")}
            )

        return attrs

    def save(self):
        self.user.has_confirmed_email = True
        self.user.save()
