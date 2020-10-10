from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from users.managers import UserManager

class User(AbstractBaseUser, PermissionsMixin):
    """
    User model which inherits AbstractBaseuser. AbstractBaseUser provides the 
    core implementation of a user model.
    """
    email = models.EmailField(
        _('email address'),
        unique=True,
    )
    first_name = models.CharField(
        _('first name'),
        max_length=255,
        unique=False,
    )
    last_name = models.CharField(
        _('last name'),
        max_length=255,
        unique=False,
    )
    phone_number = models.CharField(max_length=30)
    has_confirmed_email = models.BooleanField(default=False)
    street_address = models.CharField(
        _('street name'),
        max_length=255,
        unique=False
    )
    zip_code = models.CharField(
        _('zip code'),
        max_length = 20,
        unique = False,
    )
    zip_place = models.CharField(
        _('postal place'),
        max_length = 255,
        unique = False,
    )
    disabled_emails = models.BooleanField(
        _('disabled email'),
        default=False,
        help_text=_(
            'Decides if a user receives email from us. '
            'Typically used if we do not want a user to receive marketing (competetors).'
        ),
    )
    subscribed_to_newsletter = models.BooleanField(
        _('subscribed to newsletter'),
        default=True,
        help_text=_('Decides if a user receives marketing emails from us.'),
    )
    allow_personalization = models.BooleanField(
        _('allows personalization'),
        default=True,
        help_text=_('Decides if a user accepts a personalized experience within the app.'),
    )
    allow_third_party_personalization = models.BooleanField(
        _('allows third party personalization'),
        default=True,
        help_text=_(
            'Decides if we share user cookies with external sources such as Facebook. '
            'This will make the user see adverts and other related content to the app.'
        ),
    )
    acquisition_source = models.CharField(
        _('acquisition source'),
        blank = True,
        max_length = 255,
        unique = False,
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts if you want to preserve the data.'
        ),
    )
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_superuser = models.BooleanField(
        _('superuser status'),
        default=False,
        help_text=_('Designates whether the user is automatically granted all permissions.'),
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name= _('user')
        verbose_name_plural = _('users')
        permissions = (
            ('has_users_list', 'Can list users'),
            ('has_users_export', 'Can export users list to pdf'),
            ('has_user_add', 'Can add new users'),
        )

    def __str__(self):
        return '%s %s' % (self.first_name, self.last_name)

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """
        Return the first_name of the user
        """
        return self.first_name

    def get_address(self):
        """
        Return the full address containing streetname, zip code and place
        """
        address = '%s, %s %s' % (self.street_address, self.zip_code, self.zip_place)
        return address.strip()