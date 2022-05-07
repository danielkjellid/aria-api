import random

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.managers import CurrentSiteManager
from django.contrib.sites.models import Site
from django.core import signing
from django.core.mail import send_mail
from django.db import models
from django.forms import ValidationError
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.encoding import force_bytes, force_str
from django.utils.http import (
    urlsafe_base64_decode as uid_decoder,
    urlsafe_base64_encode as uid_encoder,
)
from django.utils.translation import gettext_lazy as _

import phonenumbers

from aria.users.enums import AvatarColors
from aria.users.managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    """
    User model which inherits AbstractBaseuser. AbstractBaseUser provides the
    core implementation of a user model.
    """

    email = models.EmailField(
        unique=True,
    )
    first_name = models.CharField(
        max_length=255,
        unique=False,
    )
    last_name = models.CharField(
        max_length=255,
        unique=False,
    )
    birth_date = models.DateField(null=True, blank=True)
    avatar_color = models.CharField(
        max_length=8,
        unique=False,
        choices=AvatarColors.choices,
    )
    phone_number = models.CharField(max_length=30)
    has_confirmed_email = models.BooleanField(default=False)
    street_address = models.CharField(max_length=255, unique=False)
    zip_code = models.CharField(
        max_length=20,
        unique=False,
    )
    zip_place = models.CharField(
        max_length=255,
        unique=False,
    )
    disabled_emails = models.BooleanField(
        default=False,
        help_text=(
            "Decides if a user receives email from us. "
            "Typically used if we do not want a user to receive marketing (competetors)."
        ),
    )
    subscribed_to_newsletter = models.BooleanField(
        default=True,
        help_text=("Decides if a user receives marketing emails from us."),
    )
    allow_personalization = models.BooleanField(
        default=True,
        help_text=(
            "Decides if a user accepts a personalized experience within the app."
        ),
    )
    allow_third_party_personalization = models.BooleanField(
        default=True,
        help_text=(
            "Decides if we share user cookies with external sources such as Facebook. "
            "This will make the user see adverts and other related content to the app."
        ),
    )
    acquisition_source = models.CharField(
        blank=True, max_length=255, unique=False, null=True
    )
    date_joined = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(
        default=True,
        help_text=(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts if you want to preserve the data."
        ),
    )
    is_staff = models.BooleanField(
        default=False,
        help_text=("Designates whether the user can log into this admin site."),
    )
    is_superuser = models.BooleanField(
        default=False,
        help_text=(
            "Designates whether the user is automatically granted all permissions."
        ),
    )
    site = models.ForeignKey(Site, on_delete=models.SET_NULL, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()
    on_site = CurrentSiteManager()

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"
        unique_together = (("email", "site"),)
        permissions = (
            ("has_users_list", "Can list users"),
            ("has_user_edit", "Can edit a single user instance"),
            ("has_user_add", "Can add a single user instance"),
            ("has_user_delete", "Can delete a single user instance"),
        )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    #################
    # Personal info #
    #################

    @property
    def full_name(self) -> str:
        """
        Return the first_name plus the last_name, with a space in between.
        """

        return f"{self.first_name} {self.last_name}"

    @property
    def short_name(self) -> str:
        """
        Return the first_name of the user
        """

        return self.first_name

    @property
    def initial(self) -> str:
        """
        Return initial for first name of user
        """

        initial = ""

        if self.first_name:
            initial = self.first_name[0].upper()

        return initial

    @property
    def full_address(self) -> str:
        """
        Return the full address containing streetname, zip code and place
        """

        return f"{self.street_address}, {self.zip_code} {self.zip_place}"

    @property
    def formatted_phone_number(self) -> str:
        """
        Returns a formatted version of the phone number
        """
        try:
            parsed_number = phonenumbers.parse(self.phone_number, "NO")

            return phonenumbers.format_number(
                parsed_number, phonenumbers.PhoneNumberFormat.NATIONAL
            )
        except Exception:
            # If we're unable to parse, return raw number.
            return self.phone_number

    @property
    def uid(self) -> str:
        """
        A users UID based on id.
        """

        return uid_encoder(force_bytes(self.id))

    #########
    # Notes #
    #########

    def get_notes(self):
        """
        Return notes related to the user.
        """

        from aria.notes.models import NoteEntry

        return NoteEntry.objects.filter(
            content_type=ContentType.objects.get_for_model(self), object_id=self.id
        )

    ##############
    # Audit logs #
    ##############

    def get_audit_logs(self):
        """
        Return audit logs related to the user.
        """

        from aria.audit_logs.models import LogEntry

        return LogEntry.objects.filter(
            content_type=ContentType.objects.get_for_model(self), object_id=self.id
        )

    #########
    # Email #
    #########

    def email_user(self, subject, message, from_email=None, **kwargs):
        """
        Send an email to this user.
        """
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def send_password_reset_email(self, *, request) -> None:
        from django.contrib.auth.forms import PasswordResetForm

        form = PasswordResetForm({"email": self.email})

        if not self.has_confirmed_email and not self.is_active:
            return None

        email_options = {
            "use_https": request.is_secure(),
            "from_email": settings.DEFAULT_FROM_EMAIL,
            "request": request,
            "email_template_name": "email/password_reset_email.html",
            "html_email_template_name": "email/password_reset_email.html",
        }

        if form.is_valid():
            form.save(**email_options)

    def validate_uid(self, uid) -> bool:
        """
        Validates a given user uid.
        """
        decoded_uid = force_str(uid_decoder(uid))

        if decoded_uid == self.id:
            return True

        return False

    def generate_verification_email_token(self) -> str:
        """
        Generates a signed token, used to verify the user's email address.
        """

        return signing.dumps({"email": self.email}, salt="users.email.verification")

    def validate_verification_email_token(self, token) -> bool:
        """
        Checks the email verification token provided by the user (included in an email).
        """

        try:
            value = signing.loads(
                token,
                max_age=settings.PASSWORD_RESET_TIMEOUT,
                salt="users.email.verification",
            )
        except signing.BadSignature:
            return False

        if value.get("email") == self.email:
            return True

        return False

    def send_verification_email(self) -> None:
        """
        Send a verification email to verify user's email address.
        """

        if self.has_confirmed_email:
            raise ValidationError(
                _("Email is already verified, unable to send verification email.")
            )

        user_verification_email = render_to_string(
            "email/verify_account.html",
            {
                "protocol": "https",
                "domain": "flis.no",
                "user": self,
                "uid": self.uid,
                "token": self.generate_verification_email_token(),
            },
        )

        self.email_user(
            "Bekreft kontoen din på Flishuset",
            "Bekreft kontoen din på Flishuset",
            html_message=user_verification_email,
        )

    def save(self, *args, **kwargs):
        if not self.avatar_color:
            self.avatar_color = random.choice(AvatarColors.choices)[0]

        super(User, self).save(*args, **kwargs)
