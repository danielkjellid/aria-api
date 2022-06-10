from decimal import Decimal

from django.contrib.sites.managers import CurrentSiteManager
from django.contrib.sites.models import Site
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from mptt.models import TreeManyToManyField

from aria.categories.models import Category
from aria.core.fields import ChoiceArrayField
from aria.core.models import (
    BaseFileModel,
    BaseHeaderImageModel,
    BaseImageModel,
    BaseModel,
    BaseThumbnailImageModel,
)
from aria.core.utils import get_array_field_labels
from aria.products import enums
from aria.products.managers import (
    ColorQuerySet,
    ProductFileQuerySet,
    ProductImageQuerySet,
    ProductOptionQuerySet,
    ProductQuerySet,
    ProductSiteStateQuerySet,
    ShapeQuerySet,
    SizeQuerySet,
    VariantQuerySet,
)
from aria.suppliers.models import Supplier

_SizeManager = models.Manager.from_queryset(SizeQuerySet)


class Size(models.Model):
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
                name="size_combo_unique",
            )
        ]

    def __str__(self) -> str:
        if (
            self.depth is not None
            and self.width is not None
            and self.height is not None
            and self.circumference is None
        ):
            return f"B{self.convert_to_self_repr(self.width)} x H{self.convert_to_self_repr(self.height)} x D{self.convert_to_self_repr(self.depth)}"

        if (
            self.circumference is not None
            and self.width is None
            and self.height is None
            and self.depth is None
        ):
            return f"Ø{self.convert_to_self_repr(self.circumference)}"

        return f"B{self.convert_to_self_repr(self.width)} x H{self.convert_to_self_repr(self.height)}"

    @property
    def name(self) -> str:
        return self.__str__()

    @staticmethod
    def convert_to_self_repr(n: Decimal | None) -> str | None:
        """
        Returns a whole number if decimals is .0
        """

        return str(round(n, 1) if n % 1 else int(n)) if n else None


_VariantManager = models.Manager.from_queryset(VariantQuerySet)


class Variant(BaseThumbnailImageModel):
    """
    A variant is another version of the product, for
    example color, pattern etc.
    """

    @property
    def variant_upload_path(self) -> str:
        return f"media/products/variants/{self.id}-{slugify(self.name)}/"

    UPLOAD_PATH = variant_upload_path  # type: ignore

    name = models.CharField(
        "product variant name",
        max_length=255,
    )
    image = ImageSpecField(
        source="thumbnail",
        processors=[ResizeToFill(80, 80)],
        format="JPEG",
        options={"quality": 90},
    )
    is_standard = models.BooleanField(
        "standard",
        default=False,
        help_text="Designates if a variant should be treated as standard. This is to avoid multiple instances of the same variant. This field will also prevent cleanup deletion of these models.",
    )

    objects = _VariantManager()

    class Meta:
        verbose_name = "Variant"
        verbose_name_plural = "Variants"

    def __str__(self) -> str:
        return self.name


_ColorManager = models.Manager.from_queryset(ColorQuerySet)


class Color(models.Model):
    """
    Color categories bellonging to products. Used for
    filtering frontend.
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


class Shape(BaseImageModel):
    """
    Shape bellonging to a product. Used for filtering frontend.
    """

    @property
    def shape_upload_path(self) -> str:
        return f"media/products/sizes/{slugify(self.name)}/"

    UPLOAD_PATH = shape_upload_path  # type: ignore

    name = models.CharField("name", max_length=30, unique=True)

    objects = _ShapeManager()

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = "Shape"
        verbose_name_plural = "Shapes"


_ProductManager = models.Manager.from_queryset(ProductQuerySet)


class Product(BaseModel, BaseThumbnailImageModel):
    """
    Product model, containing all relevant fields for products
    in the store.
    """

    @property
    def product_directory(self) -> str:
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
        help_text="A slug is a short label for something, containing only letters, numbers, underscores or hyphens. They’re generally used in URLs.",
    )
    search_keywords = models.CharField(
        "search keywords",
        max_length=255,
        unique=False,
        blank=True,
        null=True,
    )
    short_description = models.TextField(
        "short description",
        help_text="The short description will be displayed on the top part of the product, above the variant selection",
        null=True,
    )
    description = models.TextField("description", null=True)
    new_description = models.TextField("new description")
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
    colors = models.ManyToManyField("products.Color", related_name="products")
    shapes = models.ManyToManyField(
        "products.Shape", related_name="products", blank=True
    )
    materials = ChoiceArrayField(
        models.CharField(choices=enums.ProductMaterials.choices, max_length=50),
        null=True,
        help_text="Material product is made of. Want to add more options? Reach out to Daniel.",
    )
    rooms = ChoiceArrayField(
        models.CharField(choices=enums.ProductRooms.choices, max_length=50),
        null=True,
        help_text="Rooms applicable to product.",
    )
    absorption = models.FloatField(null=True, blank=True)
    sites = models.ManyToManyField(Site, related_name="products", blank=True)
    is_imported_from_external_source = models.BooleanField(default=False)
    # display_price = models.BooleanField(
    #     "display price to customer",
    #     default=True,
    #     help_text="Designates whether the product price is displayed",
    # )
    # can_be_purchased_online = models.BooleanField(
    #     "can be purchased online",
    #     default=False,
    #     help_text="Designates whether the product can be purchased and shipped",
    # )
    # can_be_picked_up = models.BooleanField(
    #     "can be picked up",
    #     default=False,
    #     help_text="Designates whether the product can be purchased and picked up in store",
    # )
    # supplier_purchase_price = models.DecimalField(
    #     "supplier purchase price", decimal_places=2, max_digits=10, default=0.00
    # )
    # supplier_shipping_cost = models.DecimalField(
    #     "shipping cost", decimal_places=2, max_digits=10, default=0.0
    # )

    objects = _ProductManager()  # type: ignore

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        permissions = (
            ("has_products_list", "Can list products"),
            ("has_product_edit", "Can edit a single product instance"),
            ("has_product_add", "Can add a single product instance"),
            ("has_product_delete", "Can delete a single product instance"),
        )

    def __str__(self) -> str:
        return self.name

    @property
    def materials_display(self) -> list[dict[str, str] | None]:
        return get_array_field_labels(self.materials, enums.ProductMaterials)

    @property
    def rooms_display(self) -> list[dict[str, str] | None]:
        return get_array_field_labels(self.rooms, enums.ProductRooms)


_ProductImageManager = models.Manager.from_queryset(ProductImageQuerySet)


class ProductImage(BaseHeaderImageModel):
    """
    Images bellonging to a product. Inherits a image
    models, which creates all needed versions of the
    uploaded image.
    """

    @property
    def product_image_directory(self) -> str:
        return f"media/products/{slugify(self.product.supplier.name)}/{slugify(self.product.name)}/images"

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


class ProductFile(BaseFileModel):
    """
    A single file bellonging to a products. This is
    typically a supplier catalog etc.
    """

    @property
    def product_file_directory(self) -> str:
        return f"media/products/{slugify(self.product.supplier.name)}/{slugify(self.product.name)}/files"

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


_ProductSiteStateManager = models.Manager.from_queryset(ProductSiteStateQuerySet)


class ProductSiteState(BaseModel):
    """
    We support multiple sites from the same frontend. This
    model allow for different settings based on site.
    """

    site = models.ForeignKey(Site, on_delete=models.PROTECT, related_name="states")
    product = models.ForeignKey(
        "products.Product", on_delete=models.CASCADE, related_name="site_states"
    )
    gross_price = models.FloatField(_("Gross price"))
    display_price = models.BooleanField(
        _("Display price to customer"),
        default=True,
        help_text=_("Designates whether the product price is displayed"),
    )
    can_be_purchased_online = models.BooleanField(
        _("Can be purchased online"),
        default=False,
        help_text=_("Designates whether the product can be purchased and shipped"),
    )
    can_be_picked_up = models.BooleanField(
        _("Can be picked up"),
        default=False,
        help_text=_(
            "Designates whether the product can be purchased and picked up in store"
        ),
    )
    supplier_purchase_price = models.FloatField(
        _("Supplier purchase price"), default=0.0
    )
    supplier_shipping_cost = models.FloatField(_("Shipping cost"), default=0.0)

    objects = _ProductSiteStateManager()  # type: ignore
    on_site = CurrentSiteManager()

    class Meta:
        verbose_name = _("Product site state")
        verbose_name_plural = _("Product site states")


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
        "products.Variant",
        on_delete=models.SET_NULL,
        related_name="product_options",
        null=True,
        blank=True,
    )
    size = models.ForeignKey(
        "products.Size",
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
                name=("one_option_combo_per_variant_size"),
            )
        ]

    @property
    def vat(self) -> Decimal:
        return Decimal(self.gross_price * Decimal(self.product.vat_rate))

    def __str__(self) -> str:
        return f"{self.product} - {self.variant} - {self.size}"
