from django.contrib.sites.managers import CurrentSiteManager
from django.contrib.sites.models import Site
from django.db import models
from django.utils.text import slugify

from django_countries.fields import CountryField

from aria.core.models import BaseImageModel, BaseModel
from aria.suppliers.managers import SupplierQuerySet

_SupplierManager = models.Manager.from_queryset(SupplierQuerySet)


class Supplier(BaseModel, BaseImageModel):
    @property
    def supplier_image_directory(self) -> str:
        """Path of which to upload static assets"""
        return f"media/suppliers/logo/{slugify(self.name)}"

    UPLOAD_PATH = supplier_image_directory  # type: ignore

    name = models.CharField("Supplier name", max_length=255, unique=True)
    contact_first_name = models.CharField(
        "Contact first name", max_length=255, unique=False
    )
    contact_last_name = models.CharField(
        "Contact last name", max_length=255, unique=False
    )
    contact_email = models.EmailField(
        "Contact email address",
        unique=False,
    )
    supplier_discount = models.FloatField(
        null=True,
        blank=True,
        help_text="Supplier discount in percent. E.g. 0.2 = 20%",
    )
    origin_country = CountryField()  # type: ignore
    is_active = models.BooleanField(
        "Active",
        default=True,
        help_text="Designates whether the category should be treated as active.",
    )
    sites = models.ManyToManyField(Site, related_name="suppliers", blank=True)
    website_link = models.CharField(max_length=255)

    objects = _SupplierManager()  # type: ignore
    on_site = CurrentSiteManager()

    class Meta:
        verbose_name = "supplier"
        verbose_name_plural = "suppliers"

    def __str__(self) -> str:
        return self.name
