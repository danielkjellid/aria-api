from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from imagekit.models.fields import ProcessedImageField
from imagekit.processors import ResizeToFill

from aria.core.models import BaseHeaderImageModel, BaseListImageModel, BaseModel
from aria.kitchens.managers import KitchenQuerySet
from aria.products.enums import ProductStatus
from aria.suppliers.models import Supplier

_KitchenManager = models.Manager.from_queryset(KitchenQuerySet)


class Kitchen(BaseModel, BaseHeaderImageModel, BaseListImageModel):
    @property
    def kitchen_image_directory(self) -> str:
        return f"media/kitchens/{slugify(self.name)}"

    UPLOAD_PATH = kitchen_image_directory

    name = models.CharField(_("Kitchen name"), max_length=255, unique=True)
    supplier = models.ForeignKey(
        Supplier, on_delete=models.CASCADE, related_name="supplier"
    )
    status = models.IntegerField(
        _("Status"),
        choices=ProductStatus.choices,
        default=ProductStatus.DRAFT,
    )
    slug = models.SlugField(
        _("Slug"),
        max_length=255,
        help_text=_(
            "A slug is a short label for something, containing only letters, numbers, underscores or hyphens. They’re generally used in URLs."
        ),
    )
    thumbnail_description = models.CharField(
        _("Thumbnail description"),
        max_length=255,
        unique=False,
    )
    description = models.TextField(_("Description"))
    extra_description = models.TextField(
        _("Extra description"),
        help_text=(_("Will be displayed bellow pricing example")),
        blank=True,
        null=True,
    )
    example_from_price = models.DecimalField(
        decimal_places=2, max_digits=8, null=True, blank=True
    )
    can_be_painted = models.BooleanField(
        _("Can be painted"),
        default=False,
        help_text=_(
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
        verbose_name = _("Kitchen")
        verbose_name_plural = _("Kitchens")

    def __str__(self) -> str:
        return self.name


class SilkColor(models.Model):

    name = models.CharField(_("Kitchen silk name"), max_length=255, unique=False)
    color_hex = models.CharField(_("Color code"), max_length=7, unique=True)

    class Meta:
        verbose_name = _("Silk color")
        verbose_name_plural = _("Silk colors")

    def __str__(self) -> str:
        return self.name


class Decor(models.Model):
    @property
    def kitchen_decor_upload_path(self) -> str:
        return f"media/kitchens/decors/{slugify(self.name)}"

    UPLOAD_PATH = kitchen_decor_upload_path

    image = ProcessedImageField(
        upload_to="t",
        processors=[ResizeToFill(80, 80)],
        format="JPEG",
        options={"quality": 90},
        blank=True,
        null=True,
    )
    name = models.CharField(_("Kitchen decor name"), max_length=255, unique=False)

    class Meta:
        verbose_name = _("Decor")
        verbose_name_plural = _("Decors")

    def __str__(self) -> str:
        return self.name


class Plywood(models.Model):
    @property
    def kitchen_playwood_upload_path(self) -> str:
        return f"media/kitchens/plywoods/{slugify(self.name)}"

    UPLOAD_PATH = kitchen_playwood_upload_path

    image = ProcessedImageField(
        upload_to="t",
        processors=[ResizeToFill(80, 80)],
        format="JPEG",
        options={"quality": 90},
        blank=True,
        null=True,
    )
    name = models.CharField(_("Kitchen playwood name"), max_length=255, unique=False)

    class Meta:
        verbose_name = _("Plywood")
        verbose_name_plural = _("Plywoods")

    def __str__(self) -> str:
        return self.name


class LaminateColor(models.Model):

    name = models.CharField(_("Kitchen laminate name"), max_length=255, unique=False)
    color_hex = models.CharField(_("Color code"), max_length=7, unique=True)

    class Meta:
        verbose_name = _("Laminate color")
        verbose_name_plural = _("Laminates colors")

    def __str__(self) -> str:
        return self.name


class ExclusiveColor(models.Model):

    name = models.CharField(_("Kitchen exclusive name"), max_length=255, unique=False)
    color_hex = models.CharField(_("Color code"), max_length=7, unique=True)

    class Meta:
        verbose_name = _("Exclusive color")
        verbose_name_plural = _("Exclusive colors")

    def __str__(self):
        return self.name


class TrendColor(models.Model):

    name = models.CharField(_("Kitchen trend name"), max_length=255, unique=False)
    color_hex = models.CharField(_("Color code"), max_length=7, unique=True)

    class Meta:
        verbose_name = _("Trend color")
        verbose_name_plural = _("Trend colors")

    def __str__(self) -> str:
        return self.name
