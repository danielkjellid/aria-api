from django.contrib.sites.models import Site
from django.contrib.sites.managers import CurrentSiteManager
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from imagekit.models import ImageSpecField, ProcessedImageField
from imagekit.processors import ResizeToFill

from core.fields import ChoiceArrayField
from core.models import BaseFileModel, BaseModel, BaseHeaderImageModel, BaseThumbnailImageModel

from products import enums

from product_categorization.models import SubCategory
from suppliers.models import Supplier


class Size(models.Model):

    class Meta:
        verbose_name = _('Size')
        verbose_name_plural = _('Sizes')
        ordering = ['width', 'height', 'depth', 'circumference']

    width = models.IntegerField(
        _('Width'),
        blank=True,
        null=True,
        help_text=_(
            'width in centimeters'
        )
    )
    height = models.IntegerField(
        _('Height'),
        blank=True,
        null=True,
        help_text=_(
            'height in centimeters'
        )
    )
    depth = models.IntegerField(
        _('Depth'),
        blank=True,
        null=True,
        help_text=_(
            'depth in centimeters'
        )
    )
    circumference = models.IntegerField(
        _('Circumference'),
        blank=True,
        null=True,
        help_text=_(
            'circumference in centimeters'
        )
    )

    def __str__(self):
        if self.depth is not None and self.circumference is None and self.width is None and self.height is None:
            full_name = f'B{self.width} x H{self.height} x D{self.depth}'
            return full_name

        if self.circumference is not None:
            full_name = f'Ø{self.circumference}'
            return full_name
        
        full_name = f'B{self.width} x H{self.height}'
        return full_name


class ProductColor(models.Model):

    class Meta:
        verbose_name = _('Product color')
        verbose_name_plural = _('Product colors')

    name = models.CharField(
        _('Name'),
        max_length=100,
        unique=True
    )
    color_hex = models.CharField(
        _('Color code'),
        max_length=7,
        unique=True
    )

    def __str__(self):
        return self.name


class Product(BaseModel, BaseThumbnailImageModel):

    objects = models.Manager()
    on_site = CurrentSiteManager()

    class Meta:
        verbose_name = _('Product')
        verbose_name_plural = _('Products')
        permissions = (
            ('has_products_list', 'Can list products'),
            ('has_product_edit', 'Can edit a single product instance'),
            ('has_product_add', 'Can add a single product instance'),
            ('has_product_delete', 'Can delete a single product instance')
        )

    @property
    def product_directory(self):
        return f'media/products/{slugify(self.supplier.name)}/{slugify(self.name)}/images'

    UPLOAD_PATH = product_directory
    
    name = models.CharField(
        _('Product name'),
        max_length=255,
        unique=True
    )
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        related_name='supplier_product'
    )
    category = models.ManyToManyField(
        SubCategory,
        related_name='products'
    )
    status = models.IntegerField(
       _('Status'),
       choices=enums.ProductStatus.choices,
       default=enums.ProductStatus.DRAFT,
    )
    slug = models.SlugField(
        _('Slug'),
        max_length=255,
        help_text=_(
            'A slug is a short label for something, containing only letters, numbers, underscores or hyphens. They’re generally used in URLs.'
        ),
    )
    search_keywords = models.CharField(
        _('Search keywords'),
        max_length=255, 
        unique=False, 
        blank=True,
        null=True,
    )
    short_description = models.TextField(
        _('Short Description'),
        help_text=_(
            'The short description will be displayed on the top part of the product, above the variant selection'
        )
    )
    description = models.TextField(_('Description'))
    unit = models.IntegerField(
       _('Unit'),
       choices=enums.ProductUnit.choices,
       default=enums.ProductUnit.SQUARE_METER,
    )
    vat_rate = models.FloatField(
        _('VAT Rate'),
        default=0.25
    )
    available_in_special_sizes = models.BooleanField(
        _('Available in special sizes'),
        default=False,
        help_text=_(
            'Designates whether the product comes in sizes out of the ordinary'
        ),
    )
    colors = models.ManyToManyField(
        ProductColor,
        related_name='product_color'
    )
    styles = ChoiceArrayField(
        models.CharField(
            choices=enums.ProductStyles.choices, 
            max_length=50
        ), 
        null=True,
        help_text=_(
            'Which style the product line represent. Want to add more options? Reach out to Daniel.'
        ),
    )
    applications = ChoiceArrayField(
        models.CharField(
            choices=enums.ProductApplications.choices, 
            max_length=50
        ), 
        null=True,
        help_text=_(
            'Area of product usage. Want to add more options? Reach out to Daniel.'
        ),
    )
    materials = ChoiceArrayField(
        models.CharField(
            choices=enums.ProductMaterials.choices, 
            max_length=50
        ), 
        null=True,
        help_text=_(
            'Material product is made of. Want to add more options? Reach out to Daniel.'
        ),
    )
    absorption = models.FloatField(
        null=True,
        blank=True
    )
    sites = models.ManyToManyField(
        Site,
        related_name='product_site',
        blank=True
    )
    is_imported_from_external_source = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def _get_array_field_labels(self, field, enum):
        """
        Return a list of human readable labels for ArrayChoiceFields
        """

        if field is None:
            return []

        # TODO: Remove value as dict, done now to not mess up frontend
        return [
            {"name": item.label} for item in enum
            for f in field
            if item.value == f
        ]

    def get_materials_display(self):
        return self._get_array_field_labels(self.materials, enums.ProductMaterials)

    def get_styles_display(self):
        return self._get_array_field_labels(self.styles, enums.ProductStyles)

    def get_applications_display(self):
        return self._get_array_field_labels(self.applications, enums.ProductApplications)


class ProductSiteState(BaseModel):

    class Meta:
        verbose_name = _('Product site state')
        verbose_name_plural = _('Product site states')

    objects = models.Manager()
    on_site = CurrentSiteManager()

    site = models.ForeignKey(
        Site,
        on_delete=models.CASCADE,
        related_name='site_state'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='product_site_state'
    )
    gross_price = models.FloatField(_('Gross price'))
    display_price = models.BooleanField(
        _('Display price to customer'),
        default=True,
        help_text=_(
            'Designates whether the product price is displayed'
        ),
    )
    can_be_purchased_online = models.BooleanField(
        _('Can be purchased online'),
        default=False,
        help_text=_(
            'Designates whether the product can be purchased and shipped'
        ),
    )
    can_be_picked_up = models.BooleanField(
        _('Can be picked up'),
        default=False,
        help_text=_(
           'Designates whether the product can be purchased and picked up in store' 
        )
    )
    supplier_purchase_price = models.FloatField(
        _('Supplier purchase price'),
        default=0.0
    )
    supplier_shipping_cost = models.FloatField(
        _('Shipping cost'),
        default=0.0
    )


class ProductImage(BaseHeaderImageModel):

    class Meta:
        verbose_name = _('Product image')
        verbose_name_plural = _('Product images')

    @property
    def product_image_directory(self):
        return f'media/products/{slugify(self.product.supplier.name)}/{slugify(self.product.name)}/images'
    
    UPLOAD_PATH = product_image_directory

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images',
    )


class ProductVariant(BaseThumbnailImageModel):

    class Meta:
        verbose_name = _('Product variant')
        verbose_name_plural = _('Product variants')

    @property
    def product_variant_directory(self):
        return f'media/products/{slugify(self.product.supplier.name)}/{slugify(self.product.name)}/variants/'

    UPLOAD_PATH = product_variant_directory

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='variants',
    )
    name = models.CharField(
        _('Product variant name'),
        max_length=255,
        unique=False
    )
    status = models.IntegerField(
       _('Status'),
       choices=enums.ProductStatus.choices,
       default=enums.ProductStatus.DRAFT,
    )
    image = ImageSpecField(
        source='thumbnail', 
        processors=[ResizeToFill(80, 80)], 
        format='JPEG', 
        options={'quality': 90}
    )
    additional_cost = models.FloatField(_('Additional cost'), default=0.0)

    def __str__(self):
        return self.name


class ProductVariantSize(models.Model):

    class Meta:
        verbose_name = _('Product size')
        verbose_name_plural = _('Product sizes')

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='sizes'
    )
    size = models.ForeignKey(
        Size,
        on_delete=models.CASCADE,
        related_name='variant_sizes'
    )
    additional_cost = models.FloatField(_('Additional cost'))


    def __str__(self):
        return f'{self.product} - {self.size}'


class ProductFile(BaseFileModel):

    class Meta:
        verbose_name = _('Product file')
        verbose_name_plural = _('Product files')

    @property
    def product_file_directory(self):
        return f'media/products/{slugify(self.product.supplier.name)}/{slugify(self.product.name)}/files'

    UPLOAD_PATH = product_file_directory

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='files',
    )
    name = models.CharField(
        _('Product file name'),
        max_length=255,
        unique=False
    )

    def __str__(self):
        return self.name
