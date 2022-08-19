from django.db import models

from aria.core.models import BaseModel
from aria.discounts.managers import DiscountQuerySet

_DiscountManager = models.Manager.from_queryset(DiscountQuerySet)


class Discount(BaseModel):
    """
    Sets the discount level for one or more products. Product discounts can
    be limited for specific products or time periods.
    """

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    slug = models.SlugField(null=True)

    products = models.ManyToManyField(
        "products.Product",
        verbose_name="products",
        related_name="discounts",
        blank=True,
    )
    product_options = models.ManyToManyField(
        "products.ProductOption",
        verbose_name="product options",
        related_name="discounts",
        blank=True,
    )

    minimum_quantity = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text=(
            "The minimum product quantity for the discount to apply per orderline. "
            "E.g. take 3, pay for 2, the minimum quantity would be 3."
        ),
    )
    maximum_quantity = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text=(
            "The maximum product quantity the discount applies to per orderline "
            "E.g. max amount of 10 items per customer."
        ),
    )

    discount_gross_price = models.DecimalField(
        blank=True,
        null=True,
        max_digits=10,
        decimal_places=2,
        help_text="Override the gross retail price of products if set.",
    )
    discount_gross_percentage = models.DecimalField(
        blank=True,
        null=True,
        max_digits=10,
        decimal_places=2,
        help_text=(
            "Override the gross price of the product by this percent. "
            "E.g. 0.25 for 25% discount."
        ),
    )

    maximum_sold_quantity = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text=(
            "The maximum number of product discounts given before the discount "
            "is ended automatically."
        ),
    )
    total_sold_quantity = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="The amount of products this discount has been applied to.",
    )
    display_maximum_quantity = models.BooleanField(
        default=False,
        help_text="Display information telling customers about maximum quantity.",
    )

    active_at = models.DateTimeField(
        "Time when discount is active from",
        blank=True,
        null=True,
        help_text=(
            "When the discount should be active from. "
            "Leave empty to activate immediately."
        ),
    )
    active_to = models.DateTimeField(
        "Time when discount is active to",
        blank=True,
        null=True,
        help_text=(
            "When the discount should end. "
            "Leave emtpy to apply discount indefinitely."
        ),
    )

    ordering = models.IntegerField(
        null=True,
        help_text=(
            "Used to order product discounts. If unset, "
            "product discounts will be ordered by the time of creation."
        ),
    )

    objects = _DiscountManager()

    class Meta:
        verbose_name = "Discount"
        verbose_name_plural = "Discounts"

    def __str__(self) -> str:
        return self.name
