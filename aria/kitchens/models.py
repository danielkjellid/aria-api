from django.db import models
from django.utils.text import slugify

from aria.core.models import BaseModel
from aria.files.models import (
    BaseCollectionListImageModel,
    BaseHeaderImageModel,
    BaseThumbnailImageModel,
)
from aria.kitchens.managers import KitchenQuerySet
from aria.products.enums import ProductStatus
from aria.suppliers.models import Supplier

_KitchenManager = models.Manager.from_queryset(KitchenQuerySet)


class Kitchen(BaseModel, BaseHeaderImageModel, BaseCollectionListImageModel):
    """
    A representation of a kitchen line we sell.
    """

    @property
    def kitchen_image_directory(self) -> str:
        """Path of which to upload static assets."""
        return f"media/kitchens/{slugify(self.name)}"

    UPLOAD_PATH = kitchen_image_directory  # type: ignore

    name = models.CharField("Kitchen name", max_length=255, unique=True)
    supplier = models.ForeignKey(
        Supplier, on_delete=models.CASCADE, related_name="supplier"
    )
    status = models.IntegerField(
        "Status",
        choices=ProductStatus.choices,
        default=ProductStatus.DRAFT,
    )
    slug = models.SlugField(
        "Slug",
        max_length=255,
        help_text=(
            "A slug is a short label for something, containing only letters, "
            "numbers, underscores or hyphens. They’re generally used in URLs."
        ),
    )
    thumbnail_description = models.CharField(
        "Thumbnail description",
        max_length=255,
        unique=False,
    )
    description = models.TextField("Description")
    extra_description = models.TextField(
        "Extra description",
        help_text="Will be displayed bellow pricing example",
        blank=True,
        null=True,
    )
    example_from_price = models.DecimalField(
        decimal_places=2, max_digits=8, null=True, blank=True
    )
    can_be_painted = models.BooleanField(
        "Can be painted",
        default=False,
        help_text=(
            "Designates whether the product can be painted in suppliers 2000 colors"
        ),
    )
    silk_variants = models.ManyToManyField(
        "kitchens.SilkColor", related_name="kitchens", blank=True
    )
    decor_variants = models.ManyToManyField(
        "kitchens.Decor", related_name="kitchens", blank=True
    )
    plywood_variants = models.ManyToManyField(
        "kitchens.Plywood", related_name="kitchens", blank=True
    )
    laminate_variants = models.ManyToManyField(
        "kitchens.LaminateColor", related_name="kitchens", blank=True
    )
    exclusive_variants = models.ManyToManyField(
        "kitchens.ExclusiveColor", related_name="kitchens", blank=True
    )
    trend_variants = models.ManyToManyField(
        "kitchens.TrendColor", related_name="kitchens", blank=True
    )

    objects = _KitchenManager()

    class Meta:
        verbose_name = "Kitchen"
        verbose_name_plural = "Kitchens"

    def __str__(self) -> str:
        return self.name


class SilkColor(models.Model):
    """
    Silk colors is a range of different colors offered by our kitchen supplier.
    """

    name = models.CharField("Kitchen silk name", max_length=255, unique=False)
    color_hex = models.CharField("Color code", max_length=7, unique=True)

    class Meta:
        verbose_name = "Silk color"
        verbose_name_plural = "Silk colors"

    def __str__(self) -> str:
        return self.name


class Decor(BaseThumbnailImageModel):
    """
    Plywood is a range of different color patterns offered by our kitchen supplier.
    """

    def kitchen_decor_upload_path(self) -> str:
        """Path of which to upload static assets."""
        return f"media/kitchens/decors/{slugify(self.name)}"

    name = models.CharField("Kitchen decor name", max_length=255, unique=False)

    class Meta:
        verbose_name = "Decor"
        verbose_name_plural = "Decors"

    def __str__(self) -> str:
        return self.name


class Plywood(BaseThumbnailImageModel):
    """
    Plywood is a range of different plywoods offered by our kitchen supplier.
    """

    def kitchen_plywood_upload_path(self) -> str:
        """Path of which to upload static assets."""
        return f"media/kitchens/plywoods/{slugify(self.name)}"

    UPLOAD_PATH = kitchen_plywood_upload_path

    name = models.CharField("Kitchen playwood name", max_length=255, unique=False)

    class Meta:
        verbose_name = "Plywood"
        verbose_name_plural = "Plywoods"

    def __str__(self) -> str:
        return self.name


class LaminateColor(models.Model):
    """
    Laminate colors is range of colors offered by the kitchen supplier.
    """

    name = models.CharField("Kitchen laminate name", max_length=255, unique=False)
    color_hex = models.CharField("Color code", max_length=7, unique=True)

    class Meta:
        verbose_name = "Laminate color"
        verbose_name_plural = "Laminates colors"

    def __str__(self) -> str:
        return self.name


class ExclusiveColor(models.Model):
    """
    Exclusive colors is a range of colors offered by the kitchen supplier.
    """

    name = models.CharField("Kitchen exclusive name", max_length=255, unique=False)
    color_hex = models.CharField("Color code", max_length=7, unique=True)

    class Meta:
        verbose_name = "Exclusive color"
        verbose_name_plural = "Exclusive colors"

    def __str__(self) -> str:
        return self.name


class TrendColor(models.Model):
    """
    Trend colors is a range of colors offered by the kitchen supplier.
    """

    name = models.CharField("Kitchen trend name", max_length=255, unique=False)
    color_hex = models.CharField("Color code", max_length=7, unique=True)

    class Meta:
        verbose_name = "Trend color"
        verbose_name_plural = "Trend colors"

    def __str__(self) -> str:
        return self.name
