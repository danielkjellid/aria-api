from django.contrib.sites.models import Site
from django.contrib.sites.managers import CurrentSiteManager
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from imagekit.models import ImageSpecField, ProcessedImageField
from imagekit.processors import ResizeToFill

from core.fields import ChoiceArrayField

from products import enums

from product_categorization.models import SubCategory
from suppliers.models import Supplier


class Size(models.Model):
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

    class Meta:
        verbose_name = _('Size')
        verbose_name_plural = _('Sizes')
        ordering = ['width', 'height', 'depth', 'circumference']

    def __str__(self):
        if self.depth is not None and self.circumference is None and self.width is None and self.height is None:
            full_name = 'B%s x H%s x D%s' % (self.width, self.height, self.depth)
            return full_name.strip()

        if self.circumference is not None:
            full_name = 'Ø%s' % (self.circumference)
            return full_name.strip()
        
        full_name = 'B%s x H%s' % (self.width, self.height)
        return full_name.strip()


class ProductColor(models.Model):
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

    class Meta:
        verbose_name = _('Product color')
        verbose_name_plural = _('Product colors')

    def __str__(self):
        return self.name.strip()


class ProductStyle(models.Model):
    name = models.CharField(
        _('Name'),
        max_length=100,
        unique=True
    )

    class Meta:
        verbose_name = _('Product style')
        verbose_name_plural = _('Product styles')

    def __str__(self):
        return self.name.strip()


class ProductApplication(models.Model):
    name = models.CharField(
        _('Name'),
        max_length=100,
        unique=True
    )

    class Meta:
        verbose_name = _('Product application')
        verbose_name_plural = _('Product applications')

    def __str__(self):
        return self.name.strip()


class ProductMaterial(models.Model):
    name = models.CharField(
        _('Name'),
        max_length=100,
        unique=True
    )

    class Meta:
        verbose_name = _('Product material')
        verbose_name_plural = _('Product materials')

    def __str__(self):
        return self.name.strip()


class Product(models.Model):

    class Unit(models.IntegerChoices):
        SQUARE_METER = 1, _('m2')
        PCS = 2, _('stk')

    def product_directory_path(self, filename):
        """
        Method to upload the files to the appropriate path
        """
        
        return 'media/products/{0}/{1}/images/{2}'.format(slugify(self.supplier.name), slugify(self.name), filename)

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
       choices=Unit.choices,
       default=Unit.SQUARE_METER,
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
    temp_styles = ChoiceArrayField(models.CharField(choices=enums.ProductStyles.choices, max_length=50), null=True)
    styles = models.ManyToManyField(
        ProductStyle,
        related_name='product_style'
    )
    temp_applications = ChoiceArrayField(models.CharField(choices=enums.ProductApplications.choices, max_length=50), null=True)
    applications = models.ManyToManyField(
        ProductApplication,
        related_name='product_application'
    )
    temp_materials = ChoiceArrayField(models.CharField(choices=enums.ProductMaterials.choices, max_length=50), null=True)
    materials = models.ManyToManyField(
        ProductMaterial,
        related_name='product_material'
    )
    absorption = models.FloatField(
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(
        _('Date created'), 
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        _('Date updated'),
        auto_now=True
    )
    thumbnail = ProcessedImageField(
        upload_to=product_directory_path,
        processors=[ResizeToFill(380, 575)],
        format='JPEG',
        options={'quality': 90},
        blank=True,
        null=True,
        default='media/products/default.jpg',
        help_text=(
            _('Image must be above 380x575px')
        )
    )
    sites = models.ManyToManyField(
        Site,
        related_name='product_site',
        blank=True
    )
    is_imported_from_external_source = models.BooleanField(default=False)
    
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

    def __str__(self):
        return self.name.strip()

    def get_materials_display(self):
        """
        Return a list of human readable labels
        """
        
        # TODO: Remove value as dict, done now to not mess up frontend
        return [
            {"name": v.label} for v in enums.ProductMaterials 
            for material in self.temp_materials 
            if v.value == material
        ]

    def get_styles_display(self):
        """
        Return a list of human readable labels
        """

        # TODO: Remove value as dict, done now to not mess up frontend
        return [
            {"name": v.label} for v in enums.ProductMaterials 
            for style in self.temp_styles 
            if v.value == style
        ]

    def get_applications_display(self):
        """
        Return a list of human readable labels
        """

        # TODO: Remove value as dict, done now to not mess up frontend
        return [
            {"name": v.label} for v in enums.ProductMaterials 
            for application in self.temp_applications 
            if v.value == application
        ]




class ProductSiteState(models.Model):
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

    objects = models.Manager()
    on_site = CurrentSiteManager()

class ProductImage(models.Model):

    def product_image_directory_path(self, filename):
        """
        Method to upload the files to the appropriate path
        """

        return 'media/products/{0}/{1}/images/{2}'.format(slugify(self.product.supplier.name), slugify(self.product.name), filename)

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images',
    )
    image = models.ImageField(
        _('Image'),
        upload_to=product_image_directory_path,
        blank=True, 
        null=True,
        help_text=(
            _('Image must be above 3072x940px')
        )
    )
    apply_filter = models.BooleanField(
        _('Apply filter'),
        default=False,
        help_text=_(
            'Apply filter to image if the image is light to maintain an acceptable contrast'
        ),
    )
    image_512x512 = ImageSpecField(
        source='image', 
        processors=[ResizeToFill(512, 512)], 
        format='JPEG', 
        options={'quality': 90}
    )
    image_1024x1024 = ImageSpecField(
        source='image', 
        processors=[ResizeToFill(1024, 1024)], 
        format='JPEG', 
        options={'quality': 90}
    )
    image_1024x480 = ImageSpecField(
        source='image', 
        processors=[ResizeToFill(1024, 480)], 
        format='JPEG', 
        options={'quality': 90}
    )
    image_1536x660 = ImageSpecField(
        source='image', 
        processors=[ResizeToFill(1536, 660)], 
        format='JPEG', 
        options={'quality': 90}
    )
    image_2048x800 = ImageSpecField(
        source='image', 
        processors=[ResizeToFill(2048, 800)], 
        format='JPEG', 
        options={'quality': 90}
    )
    image_2560x940 = ImageSpecField(
        source='image', 
        processors=[ResizeToFill(2560, 940)], 
        format='JPEG', 
        options={'quality': 90}
    )
    image_3072x940 = ImageSpecField(
        source='image', 
        processors=[ResizeToFill(3072, 940)], 
        format='JPEG', 
        options={'quality': 90}
    )

    class Meta:
        verbose_name = _('Product image')
        verbose_name_plural = _('Product images')


class ProductVariant(models.Model):

    def product_variant_directory_path(self, filename):
        """
        Method to upload the files to the appropriate path
        """

        return 'media/products/{0}/{1}/variants/{2}'.format(slugify(self.product.supplier.name), slugify(self.product.name), filename)

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
    thumbnail = ProcessedImageField(
        upload_to=product_variant_directory_path,
        processors=[ResizeToFill(380, 575)],
        format='JPEG',
        options={'quality': 90},
        blank=True,
        null=True,
        help_text=(
            _('Image must be above 380x575px')
        )
    )
    image = ImageSpecField(
        source='thumbnail', 
        processors=[ResizeToFill(80, 80)], 
        format='JPEG', 
        options={'quality': 90}
    )
    additional_cost = models.FloatField(_('Additional cost'))

    class Meta:
        verbose_name = _('Product variant')
        verbose_name_plural = _('Product variants')

    def __str__(self):
        return self.name.strip()


class ProductVariantSize(models.Model):
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

    class Meta:
        verbose_name = _('Product size')
        verbose_name_plural = _('Product sizes')

    def __str__(self):
        return '%s - %s' % (self.product, self.size)


class ProductFile(models.Model):

    def product_file_directory_path(self, filename):
        """
        Method to upload the files to the appropriate path
        """

        return 'media/products/{0}/{1}/files/{2}'.format(slugify(self.product.supplier.name), slugify(self.product.name), filename)

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
    file = models.FileField(
        _('File'),
        upload_to=product_file_directory_path
    )

    class Meta:
        verbose_name = _('Product file')
        verbose_name_plural = _('Product files')

    def __str__(self):
        return self.name.strip()
