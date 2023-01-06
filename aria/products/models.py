from decimal import Decimal

from django.db import models
from django.utils.text import slugify

from mptt.models import TreeManyToManyField

from aria.categories.models import Category
from aria.core.fields import ChoiceArrayField
from aria.core.models import BaseModel
from aria.core.records import BaseArrayFieldLabelRecord
from aria.core.utils import get_array_field_labels
from aria.files.models import (
    BaseFileModel,
    BaseHeaderImageModel,
    BaseThumbnailImageModel,
)
from aria.products import enums
from aria.products.managers import (
    ProductFileQuerySet,
    ProductImageQuerySet,
    ProductOptionQuerySet,
    ProductQuerySet,
)
from aria.suppliers.models import Supplier

_ProductManager = models.Manager.from_queryset(ProductQuerySet)


class Product(BaseModel, BaseThumbnailImageModel):
    """
    Product model, containing all relevant fields for products
    in the store.
    """

    @property
    def product_directory(self) -> str:
        """Path of which to upload static assets"""
        return (
            f"media/products/{slugify(self.supplier.name)}/{slugify(self.name)}/images"
        )

    UPLOAD_PATH = product_directory  # type: ignore

    name = models.CharField("product name", max_length=255, unique=False)
    supplier = models.ForeignKey(
        Supplier, on_delete=models.PROTECT, related_name="products"
    )
    categories = TreeManyToManyField(Category, related_name="products")
    status = models.IntegerField(
        "status",
        choices=enums.ProductStatus.choices,
        default=enums.ProductStatus.DRAFT,
    )
    slug = models.SlugField(
        "slug",
        max_length=255,
        help_text=(
            "A slug is a short label for something, containing only letters, "
            "numbers, underscores or hyphens. They’re generally used in URLs."
        ),
    )
    search_keywords = models.CharField(
        "search keywords",
        max_length=255,
        unique=False,
        blank=True,
        null=True,
    )
    description = models.TextField("description")
    unit = models.IntegerField(
        "unit",
        choices=enums.ProductUnit.choices,
        default=enums.ProductUnit.SQUARE_METER,
    )
    vat_rate = models.FloatField("VAT rate", default=0.25)
    available_in_special_sizes = models.BooleanField(
        "available in special sizes",
        default=False,
        help_text="Designates whether the product comes in sizes out of the ordinary",
    )
    colors = models.ManyToManyField(
        "product_attributes.Color", related_name="products", blank=True
    )
    shapes = models.ManyToManyField(
        "product_attributes.Shape", related_name="products", blank=True
    )
    new_materials = models.ManyToManyField(
        "product_attributes.Material", related_name="products", blank=True
    )
    materials = ChoiceArrayField(
        models.CharField(choices=enums.ProductMaterials.choices, max_length=50),
        blank=True,
        null=True,
        help_text=(
            "Material product is made of. Want to add more options? "
            "Reach out to Daniel.",
        ),
    )
    rooms = ChoiceArrayField(
        models.CharField(choices=enums.ProductRooms.choices, max_length=50),
        blank=True,
        null=True,
        help_text="Rooms applicable to product.",
    )
    new_rooms = models.ManyToManyField(
        "product_attributes.Room", related_name="products", blank=True
    )
    absorption = models.FloatField(null=True, blank=True)
    is_imported_from_external_source = models.BooleanField(default=False)
    display_price = models.BooleanField(
        "display price to customer",
        default=True,
        help_text="Designates whether the product price is displayed",
    )
    can_be_purchased_online = models.BooleanField(
        "can be purchased online",
        default=False,
        help_text="Designates whether the product can be purchased and shipped",
    )
    can_be_picked_up = models.BooleanField(
        "can be picked up",
        default=False,
        help_text=(
            "Designates whether the product can be purchased and picked up in store"
        ),
    )

    objects = _ProductManager()

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        permissions = [
            (
                "product.view",
                "Has access to view limited info about a product.",
            ),
            (
                "product.management",
                "Has access to manage products (add, edit, etc).",
            ),
            (
                "product.admin",
                "Has admin access to all product functionality, including all info.",
            ),
        ]

    def __str__(self) -> str:
        return self.name

    @property
    def materials_display(self) -> list[BaseArrayFieldLabelRecord]:
        """
        Takes the array field and turns it into a list of dicts, with
        key name and field value.

        E.g. [{"name": val}, ...]
        """
        return get_array_field_labels(self.materials, enums.ProductMaterials)

    @property
    def rooms_display(self) -> list[BaseArrayFieldLabelRecord]:
        """
        Takes the array field and turns it into a list of dicts, with
        key name and field value.

        E.g. [{"name": val}, ...]
        """
        return get_array_field_labels(self.rooms, enums.ProductRooms)

    @property
    def unit_display(self) -> str:
        """
        Get human representation of unit label.
        """
        return enums.ProductUnit(self.unit).label

    @property
    def status_display(self):
        """
        Get human readable status label.
        """
        return self.get_status_display()

    @property
    def from_price(self) -> Decimal:
        """
        Get a product's from price based on lowest possible price from
        related options.
        """

        from aria.products.selectors.pricing import product_get_price_from_options

        return product_get_price_from_options(product=self)


_ProductImageManager = models.Manager.from_queryset(ProductImageQuerySet)


class ProductImage(BaseModel, BaseHeaderImageModel):
    """
    Images belonging to a product. Inherits an image
    models, which creates all needed versions of the
    uploaded image.
    """

    @property
    def product_image_directory(self) -> str:
        """Path of which to upload static assets"""
        return (
            f"media/products/{slugify(self.product.supplier.name)}"
            f"/{slugify(self.product.name)}/images"
        )

    UPLOAD_PATH = product_image_directory  # type: ignore

    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="images",
    )

    objects = _ProductImageManager()

    class Meta:
        verbose_name = "Product image"
        verbose_name_plural = "Product images"


_ProductFileManager = models.Manager.from_queryset(ProductFileQuerySet)


class ProductFile(BaseModel, BaseFileModel):
    """
    A single file belonging to a products. This is
    typically a supplier catalog etc.
    """

    @property
    def product_file_directory(self) -> str:
        """Path of which to upload static assets"""
        return (
            f"media/products/{slugify(self.product.supplier.name)}"
            f"/{slugify(self.product.name)}/files"
        )

    UPLOAD_PATH = product_file_directory  # type: ignore

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="files",
    )
    name = models.CharField("product file name", max_length=255, unique=False)

    objects = _ProductFileManager()  # type: ignore

    class Meta:
        verbose_name = "Product file"
        verbose_name_plural = "Product files"

    def __str__(self) -> str:
        return self.name


_ProductOptionManager = models.Manager.from_queryset(ProductOptionQuerySet)


class ProductOption(BaseModel):
    """
    A combination of variant and size for a product, used
    to set the price based on selection.
    """

    product = models.ForeignKey(
        "products.Product", on_delete=models.CASCADE, related_name="options"
    )
    variant = models.ForeignKey(
        "product_attributes.Variant",
        on_delete=models.SET_NULL,
        related_name="product_options",
        null=True,
        blank=True,
    )
    size = models.ForeignKey(
        "product_attributes.Size",
        on_delete=models.PROTECT,
        related_name="product_options",
        null=True,
        blank=True,
    )
    gross_price = models.DecimalField(decimal_places=2, max_digits=8, default=0.00)
    status = models.IntegerField(
        "status",
        choices=enums.ProductStatus.choices,
        default=enums.ProductStatus.AVAILABLE,
    )

    objects = _ProductOptionManager()  # type: ignore

    class Meta:
        verbose_name = "Product option"
        verbose_name_plural = "Product options"
        constraints = [
            models.UniqueConstraint(
                fields=["product", "variant", "size"],
                name="one_option_combo_per_variant_size",
            )
        ]

    def __str__(self) -> str:
        return f"{self.product} - {self.variant} - {self.size}"

    @property
    def vat(self) -> Decimal:
        """
        Vat in amount of currency.
        """
        return Decimal(self.gross_price * Decimal(self.product.vat_rate))

    @property
    def status_display(self):
        """
        Get human readable status label.
        """
        return self.get_status_display()
