from django.db import models

from aria.suppliers.managers import SupplierManager, SupplierQuerySet


class Supplier(models.Model):
    name = models.CharField("supplier name", max_length=255, unique=True)
    contact_first_name = models.CharField(
        "contact first name", max_length=255, unique=False
    )
    contact_last_name = models.CharField(
        "contact last name", max_length=255, unique=False
    )
    contact_email = models.EmailField(
        "contact email address",
        unique=False,
    )
    supplier_discount = models.FloatField(
        null=True,
        blank=True,
        help_text="Supplier discount in percent. E.g. 0.2 = 20%",
    )
    origin_country = models.CharField("origin country", max_length=255, unique=False)
    is_active = models.BooleanField(
        "active",
        default=True,
        help_text="Designates whether the category should be treated as active.",
    )

    objects = SupplierManager.from_queryset(SupplierQuerySet)()

    class Meta:
        verbose_name = "Supplier"
        verbose_name_plural = "Suppliers"

    def __str__(self):
        return self.name
