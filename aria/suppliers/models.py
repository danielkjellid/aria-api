from django.contrib.sites.managers import CurrentSiteManager
from django.contrib.sites.models import Site
from django.db import models
from django.utils.translation import gettext_lazy as _


class Supplier(models.Model):
    name = models.CharField(_("Supplier name"), max_length=255, unique=True)
    contact_first_name = models.CharField(
        _("Contact first name"), max_length=255, unique=False
    )
    contact_last_name = models.CharField(
        _("Contact last name"), max_length=255, unique=False
    )
    contact_email = models.EmailField(
        _("Contact email address"),
        unique=False,
    )
    supplier_discount = models.FloatField(
        null=True,
        blank=True,
        help_text=_("Supplier discount in percent. E.g. 0.2 = 20%"),
    )
    origin_country = models.CharField(_("Origin country"), max_length=255, unique=False)
    is_active = models.BooleanField(
        _("Active"),
        default=True,
        help_text=_("Designates whether the category should be treated as active."),
    )
    sites = models.ManyToManyField(Site, related_name="suppliers", blank=True)

    objects = models.Manager()
    on_site = CurrentSiteManager()

    class Meta:
        verbose_name = _("supplier")
        verbose_name_plural = _("suppliers")

    def __str__(self):
        return self.name
