from django.db import models
from django.utils.translation import gettext_lazy as _


class Supplier(models.Model):
    name = models.CharField(
        _('Supplier name'),
        max_length=255,
        unique=True
    )
    contact_first_name = models.CharField(
        _('Contact first name'),
        max_length=255,
        unique=False
    )
    contact_last_name = models.CharField(
        _('Contact last name'),
        max_length=255,
        unique=False
    )
    contact_email = models.EmailField(
        _('Contact email address'),
        unique=False,
    )
    origin_country = models.CharField(
        _('Origin country'),
        max_length=255,
        unique=False
    )
    is_active = models.BooleanField(
        _('Active'),
        default=True,
        help_text=_(
            'Designates whether the category should be treated as active.'
        ),
    )

    class Meta:
        verbose_name = _('supplier')
        verbose_name_plural = _('suppliers')

    def __str__(self):
        return self.name
