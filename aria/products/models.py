from decimal import Decimal

from django.contrib.sites.managers import CurrentSiteManager
from django.contrib.sites.models import Site
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill

from aria.core.fields import ChoiceArrayField
from aria.core.models import (
    BaseFileModel,
    BaseHeaderImageModel,
    BaseModel,
    BaseThumbnailImageModel,
)
from aria.product_categorization.models import SubCategory
from aria.products import enums
from aria.suppliers.models import Supplier


class Product(BaseModel, BaseThumbnailImageModel):
    """
    Product model, containing all relevant fields for products
    in the store.
    """

    @property
    def product_directory(self):
        return (
            f"media/products/{slugify(self.supplier.name)}/{slugify(self.name)}/images"
        )

    UPLOAD_PATH = product_directory

    name = models.CharField(_("Product name"), max_length=255, unique=False)
    supplier = models.ForeignKey(
        Supplier, on_delete=models.PROTECT, related_name="products"
    )
    category = models.ManyToManyField(SubCategory, related_name="products")
    status = models.IntegerField(
        _("Status"),
        choices=enums.ProductStatus.choices,
        default=enums.ProductStatus.DRAFT,
    )
    slug = models.SlugField(
        _("Slug"),
        max_length=255,
        help_text=_(
            "A slug is a short label for something, containing only letters, numbers, underscores or hyphens. They’re generally used in URLs.",
        ),
    )
    search_keywords = models.CharField(
        _("Search keywords"),
        max_length=255,
        unique=False,
        blank=True,
        null=True,
    )
    short_description = models.TextField(
        _("Short Description"),
        help_text=_(
            "The short description will be displayed on the top part of the product, above the variant selection"
        ),
        null=True,
    )
    description = models.TextField(_("Description"))
    unit = models.IntegerField(
        _("Unit"),
        choices=enums.ProductUnit.choices,
        default=enums.ProductUnit.SQUARE_METER,
    )
    vat_rate = models.FloatField(_("VAT Rate"), default=0.25)
    available_in_special_sizes = models.BooleanField(
        _("Available in special sizes"),
        default=False,
        help_text=_(
            "Designates whether the product comes in sizes out of the ordinary"
        ),
    )
    colors = models.ManyToManyField("products.Color", related_name="products")
    styles = ChoiceArrayField(
        models.CharField(choices=enums.ProductStyles.choices, max_length=50),
        null=True,
        help_text=_(
            "Which style the product line represent. Want to add more options? Reach out to Daniel."
        ),
    )
    applications = ChoiceArrayField(
        models.CharField(choices=enums.ProductApplications.choices, max_length=50),
        null=True,
        help_text=_(
            "Area of product usage. Want to add more options? Reach out to Daniel."
        ),
    )
    materials = ChoiceArrayField(
        models.CharField(choices=enums.ProductMaterials.choices, max_length=50),
        null=True,
        help_text=_(
            "Material product is made of. Want to add more options? Reach out to Daniel."
        ),
    )
    absorption = models.FloatField(null=True, blank=True)
    sites = models.ManyToManyField(Site, related_name="products", blank=True)
    is_imported_from_external_source = models.BooleanField(default=False)

    objects = models.Manager()
    on_site = CurrentSiteManager()

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")
        permissions = (
            ("has_products_list", "Can list products"),
            ("has_product_edit", "Can edit a single product instance"),
            ("has_product_add", "Can add a single product instance"),
            ("has_product_delete", "Can delete a single product instance"),
        )

    def __str__(self):
        return self.name

    def _get_array_field_labels(self, field, enum):
        """
        Return a list of human readable labels for ArrayChoiceFields
        """

        if field is None:
            return []

        # TODO: Remove value as dict, done now to not mess up frontend
        return [{"name": item.label} for item in enum for f in field if item.value == f]

    def get_materials_display(self):
        return self._get_array_field_labels(self.materials, enums.ProductMaterials)

    def get_styles_display(self):
        return self._get_array_field_labels(self.styles, enums.ProductStyles)

    def get_applications_display(self):
        return self._get_array_field_labels(
            self.applications, enums.ProductApplications
        )


class ProductImage(BaseHeaderImageModel):
    """
    Images bellonging to a product. Inherits a image
    models, which creates all needed versions of the
    uploaded image.
    """

    @property
    def product_image_directory(self):
        return f"media/products/{slugify(self.product.supplier.name)}/{slugify(self.product.name)}/images"

    UPLOAD_PATH = product_image_directory

    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="images",
    )

    class Meta:
        verbose_name = _("Product image")
        verbose_name_plural = _("Product images")


class ProductFile(BaseFileModel):
    """
    A single file bellonging to a products. This is
    typically a supplier catalog etc.
    """

    @property
    def product_file_directory(self):
        return f"media/products/{slugify(self.product.supplier.name)}/{slugify(self.product.name)}/files"

    UPLOAD_PATH = product_file_directory

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="files",
    )
    name = models.CharField(_("Product file name"), max_length=255, unique=False)

    class Meta:
        verbose_name = _("Product file")
        verbose_name_plural = _("Product files")

    def __str__(self):
        return self.name


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

    objects = models.Manager()
    on_site = CurrentSiteManager()

    class Meta:
        verbose_name = _("Product site state")
        verbose_name_plural = _("Product site states")


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
        _("Status"),
        choices=enums.ProductStatus.choices,
        default=enums.ProductStatus.AVAILABLE,
    )

    class Meta:
        verbose_name = _("Product option")
        verbose_name_plural = _("Product options")
        constraints = [
            models.UniqueConstraint(
                fields=["product", "variant", "size"],
                name=("one_option_combo_per_variant_size"),
            )
        ]

    @property
    def vat(self):
        return self.price * self.product.vat_rate

    def __str__(self):
        return f"{self.product} - {self.variant} - {self.size}"


class Size(models.Model):
    """
    A dimension of which a product exists in.
    """

    width = models.DecimalField(
        _("width"),
        decimal_places=2,
        max_digits=6,
        blank=True,
        null=True,
        help_text=_("width in centimeters"),
    )
    height = models.DecimalField(
        _("height"),
        decimal_places=2,
        max_digits=6,
        blank=True,
        null=True,
        help_text=_("height in centimeters"),
    )
    depth = models.DecimalField(
        _("depth"),
        decimal_places=2,
        max_digits=6,
        blank=True,
        null=True,
        help_text=_("depth in centimeters"),
    )
    circumference = models.DecimalField(
        _("circumference"),
        decimal_places=2,
        max_digits=6,
        blank=True,
        null=True,
        help_text=_("circumference in centimeters"),
    )

    class Meta:
        verbose_name = _("Size")
        verbose_name_plural = _("Sizes")
        ordering = ["width", "height", "depth", "circumference"]
        constraints = [
            models.UniqueConstraint(
                fields=["width", "height", "depth", "circumference"],
                name="size_combo_unique",
            )
        ]

    def __str__(self):
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

    def convert_to_self_repr(self, n):
        """
        Returns a whole number is decimals is .0
        """

        return str(round(n, 1) if n % 1 else int(n))


class Variant(BaseThumbnailImageModel):
    """
    A variant is another version of the product, for
    example color, pattern etc.
    """

    @property
    def variant_upload_path(self):
        return f"media/products/variants/{self.id}-{slugify(self.name)}/"

    UPLOAD_PATH = variant_upload_path

    name = models.CharField(
        _("Product variant name"),
        max_length=255,
    )
    image = ImageSpecField(
        source="thumbnail",
        processors=[ResizeToFill(80, 80)],
        format="JPEG",
        options={"quality": 90},
    )
    is_standard = models.BooleanField(
        _("standard"),
        default=False,
        help_text=_('designates if a variant should be treated as standard. This is to avoid multiple instances of the same variant. This field will also prevent cleanup deletion of these models.')
    )

    class Meta:
        verbose_name = _("Variant")
        verbose_name_plural = _("Variants")

    def __str__(self):
        return self.name


class Color(models.Model):
    """
    Color categories bellonging to products. Used for
    filtering frontend.
    """

    name = models.CharField(_("Name"), max_length=100, unique=True)
    color_hex = models.CharField(_("Color code"), max_length=7, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Color")
        verbose_name_plural = _("Colors")
