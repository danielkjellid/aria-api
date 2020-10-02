import os
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from imagekit.models import ImageSpecField, ProcessedImageField
from imagekit.processors import ResizeToFill


class Category(models.Model):

    class CategoryWidth(models.TextChoices):
        FULL = 'full', _('Fullwidth')
        HALF = 'half', _('Half')

    def category_directory_path(self, filename):
        """
        Method to upload the files to the appropriate path
        """

        return 'media/categories/{0}/{1}'.format(self.name, filename)

    name = models.CharField(
        _('Category name'), 
        max_length=255, 
        unique=False
    )
    slug = models.SlugField(
        _('Slug'),
        max_length=50,
        help_text=_(
            'A slug is a short label for something, containing only letters, numbers, underscores or hyphens. They’re generally used in URLs.'
        ),
    )
    ordering = models.PositiveSmallIntegerField(
        _('Order'),
        help_text=_(
            'Order  in which the category should be displayed.'
        ),
        blank=True,
        default=0
    )
    width = models.CharField(
        _('Width'), 
        max_length=4, 
        choices=CategoryWidth.choices,
        default=CategoryWidth.FULL,
        blank=True,
        null=True,
    )
    image = models.ImageField(
        _('Image'),
        upload_to=category_directory_path,
        help_text=_(
            'Category image, should only be used on top level parents!'
        ),
        blank=True, 
        null=True,
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
    image_1536x1536 = ImageSpecField(
        source='image', 
        processors=[ResizeToFill(1536, 1536)], 
        format='JPEG', 
        options={'quality': 90}
    )
    image_1024x480 = ImageSpecField(
        source='image', 
        processors=[ResizeToFill(1024, 576)], 
        format='JPEG', 
        options={'quality': 90}
    )
    image_1536x660 = ImageSpecField(
        source='image', 
        processors=[ResizeToFill(1536, 864)], 
        format='JPEG', 
        options={'quality': 90}
    )
    image_2048x800 = ImageSpecField(
        source='image', 
        processors=[ResizeToFill(2048, 1152)], 
        format='JPEG', 
        options={'quality': 90}
    )
    image_2560x940 = ImageSpecField(
        source='image', 
        processors=[ResizeToFill(2560, 1440)], 
        format='JPEG', 
        options={'quality': 90}
    )
    image_3072x940 = ImageSpecField(
        source='image', 
        processors=[ResizeToFill(3072, 1728)], 
        format='JPEG', 
        options={'quality': 90}
    )
    display_in_navbar = models.BooleanField(
        _('Display in navigation bar'),
        default=True,
        help_text=_(
            'Designates whether the category should be displayed in the nav dropdown.'
        ),
    )
    is_active = models.BooleanField(
        _('Active'),
        default=True,
        help_text=_(
            'Designates whether the category should be treated as active.'
        ),
    )

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')

    def __str__(self):
        return self.name


class SubCategory(models.Model):

    parent = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE, 
        related_name='children', 
    )
    name = models.CharField(
        _('Category name'), 
        max_length=255, 
        unique=False
    )
    slug = models.SlugField(
        _('Slug'),
        max_length=50,
        help_text=_(
            'A slug is a short label for something, containing only letters, numbers, underscores or hyphens. They’re generally used in URLs.'
        ),
    )
    ordering = models.PositiveSmallIntegerField(
        _('Order'),
        help_text=_(
            'Order  in which the category should be displayed.'
        ),
        blank=True,
        default=0
    )
    is_active = models.BooleanField(
        _('Active'),
        default=True,
        help_text=_(
            'Designates whether the category should be treated as active.'
        ),
    )

    class Meta:
        verbose_name = _('Subcategory')
        verbose_name_plural = _('Subcategories')

    def __str__(self):
        return '%s: %s' % (self.parent, self.name)

    def get_name(self):
        return self.name.strip()


class Supplier(models.Model):
    name = models.CharField(
        _('Supplier name'),
        max_length=255,
        unique=True
    )
    contact_first_name = models.CharField(
        _('Contact first name'),
        max_length=255,
        unique=False
    )
    contact_last_name = models.CharField(
        _('Contact last name'),
        max_length=255,
        unique=False
    )
    contact_email = models.EmailField(
        _('Contact email address'),
        unique=False,
    )
    origin_country = models.CharField(
        _('Origin country'),
        max_length=255,
        unique=False
    )
    is_active = models.BooleanField(
        _('Active'),
        default=True,
        help_text=_(
            'Designates whether the category should be treated as active.'
        ),
    )

    class Meta:
        verbose_name = _('supplier')
        verbose_name_plural = _('suppliers')

    def __str__(self):
        return self.name


class ProductSize(models.Model):
    width = models.IntegerField(
        _('Width'),
        help_text=_(
            'width in centimeters'
        )
    )
    height = models.IntegerField(
        _('Height'),
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

    class Meta:
        verbose_name = _('Product size')
        verbose_name_plural = _('Product sizes')

    def __str__(self):
        if self.depth is not None:
            full_name = 'B%s x H%s x D%s' % (self.width, self.height, self.depth)
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


class Status(models.IntegerChoices):
    DRAFT = 1, _('Draft')
    HIDDEN = 2, _('Hidden')
    AVAILABLE = 3, _('Available')
    DISCONTINUED = 4, _('Discontinued')


class Units(models.IntegerChoices):
    SQUARE_METER = 1, _('m2')
    PCS = 2, _('stk')


class Product(models.Model):

    def product_directory_path(self, filename):
        """
        Method to upload the files to the appropriate path
        """

        return 'media/products/{0}/{1}'.format(self.name, filename)

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
       choices=Status.choices,
       default=Status.DRAFT,
    )
    slug = models.SlugField(
        _('Slug'),
        max_length=255,
        help_text=_(
            'A slug is a short label for something, containing only letters, numbers, underscores or hyphens. They’re generally used in URLs.'
        ),
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

       choices=Units.choices,
       default=Units.SQUARE_METER,
    )
    vat_rate = models.FloatField(
        _('VAT Rate'),
        default=0.25
    )
    gross_price = models.FloatField(_('Gross price'))
    sizes = models.ManyToManyField(
        ProductSize,
        related_name='product_size'
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
    styles = models.ManyToManyField(
        ProductStyle,
        related_name='product_style'
    )
    applications = models.ManyToManyField(
        ProductApplication,
        related_name='product_application'
    )
    materials = models.ManyToManyField(
        ProductMaterial,
        related_name='product_material'
    )
    absorption = models.FloatField(
        null=True,
        blank=True
    )
    can_be_purchased_online = models.BooleanField(
        _('Can be purchased online'),
        default=False,
        help_text=_(
            'Designates whether the product can be purchased and shipped'
        ),
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
        default='media/products/default.jpg'
    )

    class Meta:
        verbose_name = _('Product')
        verbose_name_plural = _('Products')

    def __str__(self):
        return self.name.strip()


class ProductImage(models.Model):

    def product_image_directory_path(self, filename):
        """
        Method to upload the files to the appropriate path
        """

        return 'media/products/{0}/images/{1}'.format(self.product.name, filename)

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
    image_1536x1536 = ImageSpecField(
        source='image', 
        processors=[ResizeToFill(1536, 1536)], 
        format='JPEG', 
        options={'quality': 90}
    )
    image_1024x480 = ImageSpecField(
        source='image', 
        processors=[ResizeToFill(1024, 576)], 
        format='JPEG', 
        options={'quality': 90}
    )
    image_1536x660 = ImageSpecField(
        source='image', 
        processors=[ResizeToFill(1536, 864)], 
        format='JPEG', 
        options={'quality': 90}
    )
    image_2048x800 = ImageSpecField(
        source='image', 
        processors=[ResizeToFill(2048, 1152)], 
        format='JPEG', 
        options={'quality': 90}
    )
    image_2560x940 = ImageSpecField(
        source='image', 
        processors=[ResizeToFill(2560, 1440)], 
        format='JPEG', 
        options={'quality': 90}
    )
    image_3072x940 = ImageSpecField(
        source='image', 
        processors=[ResizeToFill(3072, 1728)], 
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

        return 'media/products/{0}/variants/{1}'.format(self.product.name, filename)

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='variants',
    )
    name = models.CharField(
        _('Product variant name'),
        max_length=255,
        unique=True
    )
    status = models.IntegerField(
       _('Status'),
       choices=Status.choices,
       default=Status.DRAFT,
    )
    thumbnail = ProcessedImageField(
        upload_to=product_variant_directory_path,
        processors=[ResizeToFill(380, 575)],
        format='JPEG',
        options={'quality': 90},
        blank=True,
        null=True
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


class ProductFile(models.Model):

    def product_file_directory_path(self, filename):
        """
        Method to upload the files to the appropriate path
        """

        return 'media/products/{0}/files/{1}'.format(self.product.name, filename)

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