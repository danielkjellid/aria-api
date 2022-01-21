from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from aria.core.models import BaseHeaderImageModel, BaseModel


class Category(BaseModel, BaseHeaderImageModel):
    class CategoryWidth(models.TextChoices):
        FULL = "full", _("Fullwidth")
        HALF = "half", _("Half")

    @property
    def category_image_directory_path(self):
        return f"media/categories/{slugify(self.name)}"

    UPLOAD_PATH = category_image_directory_path

    name = models.CharField(_("Category name"), max_length=255, unique=False)
    slug = models.SlugField(
        _("Slug"),
        max_length=50,
        help_text=_(
            "A slug is a short label for something, containing only letters, numbers, underscores or hyphens. They’re generally used in URLs."
        ),
    )
    ordering = models.PositiveSmallIntegerField(
        _("Order"),
        help_text=_("Order  in which the category should be displayed."),
        blank=True,
        default=0,
    )
    width = models.CharField(
        _("Width"),
        max_length=4,
        choices=CategoryWidth.choices,
        default=CategoryWidth.FULL,
        blank=True,
        null=True,
    )
    display_in_navbar = models.BooleanField(
        _("Display in navigation bar"),
        default=True,
        help_text=_(
            "Designates whether the category should be displayed in the nav dropdown."
        ),
    )
    is_active = models.BooleanField(
        _("Active"),
        default=True,
        help_text=_("Designates whether the category should be treated as active."),
    )

    objects = models.Manager()

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

    def __str__(self):
        return self.name


class SubCategory(models.Model):

    parent = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="children",
    )
    name = models.CharField(_("Category name"), max_length=255, unique=False)
    slug = models.SlugField(
        _("Slug"),
        max_length=50,
        help_text=_(
            "A slug is a short label for something, containing only letters, numbers, underscores or hyphens. They’re generally used in URLs."
        ),
    )
    ordering = models.PositiveSmallIntegerField(
        _("Order"),
        help_text=_("Order  in which the category should be displayed."),
        blank=True,
        default=0,
    )
    is_active = models.BooleanField(
        _("Active"),
        default=True,
        help_text=_("Designates whether the category should be treated as active."),
    )

    objects = models.Manager()

    class Meta:
        verbose_name = _("Subcategory")
        verbose_name_plural = _("Subcategories")

    def __str__(self):
        return "%s: %s" % (self.parent, self.name)

    def get_name(self):
        return self.name.strip()
