from decimal import Decimal

from django.db import models
from django.utils.text import slugify

from aria.core.models import BaseModel
from aria.files.models import BaseImageModel, BaseThumbnailImageModel
from aria.product_attributes.managers import (
    ColorQuerySet,
    MaterialsQuerySet,
    RoomQuerySet,
    ShapeQuerySet,
    SizeQuerySet,
    VariantQuerySet,
)

_ColorManager = models.Manager.from_queryset(ColorQuerySet)


class Color(BaseModel):
    """
    Colors a product might exist in.
    """

    name = models.CharField("name", max_length=100, unique=True)
    color_hex = models.CharField("color code", max_length=7, unique=True)

    objects = _ColorManager()

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = "Color"
        verbose_name_plural = "Colors"


_ShapeManager = models.Manager.from_queryset(ShapeQuerySet)


class Shape(BaseImageModel, BaseModel):
    """
    Shapes a product might exist in.
    """

    @property
    def shape_upload_path(self) -> str:
        """Path of which to upload static assets"""
        return f"media/products/sizes/{slugify(self.name)}/"

    UPLOAD_PATH = shape_upload_path  # type: ignore

    name = models.CharField("name", max_length=30, unique=True)

    objects = _ShapeManager()

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = "Shape"
        verbose_name_plural = "Shapes"


_MaterialsManager = models.Manager.from_queryset(MaterialsQuerySet)


class Material(BaseModel):
    """
    A material a product is made of.
    """

    name = models.CharField("name", max_length=50, unique=True)

    objects = _MaterialsManager()

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = "Material"
        verbose_name_plural = "Materials"


_RoomManager = models.Manager.from_queryset(RoomQuerySet)


class Room(BaseModel):
    """
    A room suitable for a product.
    """

    name = models.CharField("name", max_length=50, unique=True)

    objects = _RoomManager()

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = "Room"
        verbose_name_plural = "Rooms"


_SizeManager = models.Manager.from_queryset(SizeQuerySet)


class Size(BaseModel):
    """
    A dimension of which a product exists in.
    """

    width = models.DecimalField(
        "width",
        decimal_places=2,
        max_digits=6,
        blank=True,
        null=True,
        help_text="Width in centimeters",
    )
    height = models.DecimalField(
        "height",
        decimal_places=2,
        max_digits=6,
        blank=True,
        null=True,
        help_text="Height in centimeters",
    )
    depth = models.DecimalField(
        "depth",
        decimal_places=2,
        max_digits=6,
        blank=True,
        null=True,
        help_text="Depth in centimeters",
    )
    circumference = models.DecimalField(
        "circumference",
        decimal_places=2,
        max_digits=6,
        blank=True,
        null=True,
        help_text="Circumference in centimeters",
    )

    objects = _SizeManager()

    class Meta:
        verbose_name = "Size"
        verbose_name_plural = "Sizes"
        ordering = ["width", "height", "depth", "circumference"]
        constraints = [
            models.UniqueConstraint(
                fields=["width", "height", "depth", "circumference"],
                name="size_unique",
            )
        ]

    def __str__(self) -> str:
        if self.depth and self.width and self.height and not self.circumference:
            return (
                f"B{self.convert_to_self_repr(self.width)} "
                f"x H{self.convert_to_self_repr(self.height)} "
                f"x D{self.convert_to_self_repr(self.depth)}"
            )

        if self.circumference and not self.width and not self.height and not self.depth:
            return f"Ø{self.convert_to_self_repr(self.circumference)}"

        return (
            f"B{self.convert_to_self_repr(self.width)} "
            f"x H{self.convert_to_self_repr(self.height)}"
        )

    @property
    def name(self) -> str:
        """
        Name of size, as string representation.
        """
        return self.__str__()  # pylint: disable=unnecessary-dunder-call

    @staticmethod
    def convert_to_self_repr(dec: Decimal | None) -> str | None:
        """
        Returns a whole number if decimals is .0
        """

        return str(round(dec, 1) if dec % 1 else int(dec)) if dec else None


_VariantManager = models.Manager.from_queryset(VariantQuerySet)


class Variant(BaseThumbnailImageModel, BaseModel):
    """
    A variant is another version of the product, which is not strictly connected to
    filtering attributes.

    Products are often composed of different patterns, or structures which are best
    illustrated by images, rather than colors.
    """

    @property
    def variant_upload_path(self) -> str:
        """Path of which to upload static assets"""
        return f"media/products/variants/{self.id}-{slugify(self.name)}/"

    UPLOAD_PATH = variant_upload_path  # type: ignore

    name = models.CharField(
        "product variant name",
        max_length=255,
    )
    is_standard = models.BooleanField(
        "standard",
        default=False,
        help_text=(
            "Designates if a variant should be treated as standard. "
            "This is to avoid multiple instances of the same variant. "
            "This field will also prevent cleanup deletion of these models."
        ),
    )

    objects = _VariantManager()

    class Meta:
        verbose_name = "Variant"
        verbose_name_plural = "Variants"

    def __str__(self) -> str:
        return self.name
