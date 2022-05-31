from django.contrib.sites.managers import CurrentSiteManager
from django.contrib.sites.models import Site
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from django_countries.fields import CountryField

from aria.core.models import BaseImageModel, BaseModel


class Supplier(BaseModel, BaseImageModel):
    @property
    def supplier_image_directory(self):
        return f"media/suppliers/logo/{slugify(self.name)}"

    UPLOAD_PATH = supplier_image_directory

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
    origin_country = CountryField()
    is_active = models.BooleanField(
        _("Active"),
        default=True,
        help_text=_("Designates whether the category should be treated as active."),
    )
    sites = models.ManyToManyField(Site, related_name="suppliers", blank=True)
    website_link = models.CharField(max_length=255)

    objects = models.Manager()
    on_site = CurrentSiteManager()

    class Meta:
        verbose_name = _("supplier")
        verbose_name_plural = _("suppliers")

    def __str__(self):
        return self.name


# for s in Supplier.objects.all():
#     if s.origin_country == "Italia":
#         s.origin_country = "it"
#     elif s.origin_country == "Danmark":
#         s.origin_country = "dk"
#     elif s.origin_country == "Norge":
#         s.origin_country = "no"
#     elif s.origin_country == "Nederland":
#         s.origin_country = "nl"
#     s.save()
