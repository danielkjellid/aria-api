import os
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill


class Category(models.Model):

    class CategoryWidth(models.TextChoices):
        FULL = 'full', _('Fullwidth')
        HALF = 'half', _('Half')

    name = models.CharField(
        _('category name'), 
        max_length=255, 
        unique=False
    )
    slug = models.SlugField(
        _('slug'),
        max_length=50,
        help_text=_(
            'A slug is a short label for something, containing only letters, numbers, underscores or hyphens. They’re generally used in URLs.'
        ),
    )
    ordering = models.PositiveSmallIntegerField(
        _('order'),
        help_text=_(
            'Order  in which the category should be displayed.'
        ),
        blank=True,
        default=0
    )
    width = models.CharField(
        _('width'), 
        max_length=4, 
        choices=CategoryWidth.choices,
        default=CategoryWidth.FULL,
        blank=True,
        null=True,
    )
    image = models.ImageField(
        _('image'),
        upload_to='media/categories',
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
        _('display in navigation bar'),
        default=True,
        help_text=_(
            'Designates whether the category should be displayed in the nav dropdown.'
        ),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether the category should be treated as active.'
        ),
    )

    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')

    def __str__(self):
        return self.name


class SubCategory(models.Model):
    parent = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE, 
        related_name='children', 
    )
    name = models.CharField(
        _('category name'), 
        max_length=255, 
        unique=False
    )
    slug = models.SlugField(
        _('slug'),
        max_length=50,
        help_text=_(
            'A slug is a short label for something, containing only letters, numbers, underscores or hyphens. They’re generally used in URLs.'
        ),
    )
    ordering = models.PositiveSmallIntegerField(
        _('order'),
        help_text=_(
            'Order  in which the category should be displayed.'
        ),
        blank=True,
        default=0
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether the category should be treated as active.'
        ),
    )

    class Meta:
        verbose_name = _('sub category')
        verbose_name_plural = _('sub categories')

    def __str__(self):
        return '%s > %s' % (self.parent, self.name)


class Supplier(models.Model):
    name = models.CharField(
        _('supplier name'),
        max_length=255,
        unique=True
    )
    contact_first_name = models.CharField(
        _('contact first name'),
        max_length=255,
        unique=False
    )
    contact_last_name = models.CharField(
        _('contact last name'),
        max_length=255,
        unique=False
    )
    contact_email = models.EmailField(
        _('contact email address'),
        unique=True,
    )
    origin_country = models.CharField(
        _('origin country'),
        max_length=255,
        unique=False
    )
    is_active = models.BooleanField(
        _('active'),
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
    height = models.FloatField(
        _('height'),
        help_text=_(
            'height in centimeters'
        )
    )
    width = models.FloatField(
        _('width'),
        help_text=_(
            'width in centimeters'
        )
    )
    depth = models.FloatField(
        _('depth'),
        null=True,
        help_text=_(
            'depth in centimeters'
        )
    )

    class Meta:
        verbose_name = _('product size')
        verbose_name_plural = _('product sizes')

    def __str__(self):
        if self.depth is not None:
            full_name = 'B%s x H%s x D%s' % (self.width, self.height, self.depth)
            return full_name.strip()

        full_name = 'B%s x H%s' % (self.width, self.height)
        return full_name.strip()


class ProductColor(models.Model):
    name = models.CharField(
        _('name'),
        max_length=100,
        unique=True
    )
    color_hex = models.CharField(
        _('color code'),
        max_length=7,
        unique=True
    )

    class Meta:
        verbose_name = _('product color')
        verbose_name_plural = _('product colors')

    def __str__(self):
        return self.name.strip()


class ProductRoom(models.Model):
    name = models.CharField(
        _('name'),
        max_length=100,
        unique=True
    )

    class Meta:
        verbose_name = _('product room')
        verbose_name_plural = _('product rooms')

    def __str__(self):
        return self.name.strip()


class ProductStyle(models.Model):
    name = models.CharField(
        _('name'),
        max_length=100,
        unique=True
    )

    class Meta:
        verbose_name = _('style')
        verbose_name_plural = _('styles')

    def __str__(self):
        return self.name.strip()


class ProductApplication(models.Model):
    name = models.CharField(
        _('name'),
        max_length=100,
        unique=True
    )

    class Meta:
        verbose_name = _('product application')
        verbose_name_plural = _('product applications')

    def __str__(self):
        return self.name.strip()


class ProductMaterial(models.Model):
    name = models.CharField(
        _('name'),
        max_length=100,
        unique=True
    )

    class Meta:
        verbose_name = _('product material')
        verbose_name_plural = _('product materials')

    def __str__(self):
        return self.name.strip()


class Product(models.Model):

    class ProductStatuses(models.TextChoices):
        DRAFT = 'draft', _('draft')
        AVAILABLE = 'available', _('available')
        DISCONTINUED = 'discontinued', _('discontinued')
        HIDDEN = 'hiddem', _('hidden')

    class ProductUnits(models.TextChoices):
        SQUARE_METER = 'm2', _('m2')
        PCS = 'stk', _('pcs')

    name = models.CharField(
        _('product name'),
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
    status = models.CharField(
       _('status'),
       max_length=15,
       unique=False,
       choices=ProductStatuses.choices,
       default=ProductStatuses.DRAFT,
    )
    slug = models.SlugField(
        _('slug'),
        max_length=255,
        help_text=_(
            'A slug is a short label for something, containing only letters, numbers, underscores or hyphens. They’re generally used in URLs.'
        ),
    )
    short_description = models.TextField(
        _('short description'),
        help_text=_(
            'The short description will be displayed on the top part of the product, above the variant selection'
        )
    )
    description = models.TextField(_('description'))
    unit = models.CharField(
       _('unit'),
       max_length=5,
       unique=False,
       choices=ProductUnits.choices,
       default=ProductUnits.SQUARE_METER,
    )
    vat_rate = models.FloatField(
        _('vat rate'),
        default=0.25
    )
    net_price = models.FloatField(_('net price'))
    sizes = models.ManyToManyField(
        ProductSize,
        related_name='product_size'
    )
    available_in_special_sizes = models.BooleanField(
        _('available in special sizes'),
        default=False,
        help_text=_(
            'Designates whether the product comes in sizes out of the ordinary'
        ),
    )
    colors = models.ManyToManyField(
        ProductColor,
        related_name='product_color'
    )
    rooms = models.ManyToManyField(
        ProductRoom,
        related_name='product_room'
    )
    styles = models.ManyToManyField(
        ProductStyle,
        related_name='product_style'
    )
    application = models.ManyToManyField(
        ProductApplication,
        related_name='product_application'
    )
    material = models.ManyToManyField(
        ProductMaterial,
        related_name='product_material'
    )
    absorption = models.FloatField(
        null=True,
        blank=True
    )
    can_be_purchased_online = models.BooleanField(
        _('can be purchased online'),
        default=False,
        help_text=_(
            'Designates whether the product can be purchased and shipped'
        ),
    )
    created_at = models.DateTimeField(
        _('date created'), 
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        _('date updated'),
        auto_now=True
    )

    class Meta:
        verbose_name = _('product')
        verbose_name_plural = _('products')

    def __str__(self):
        return self.name.strip()


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images',
    )
    image = models.ImageField(
        _('image'),
        upload_to='media/products/',
        help_text=_(
            'Product image'
        ),
        blank=True, 
        null=True,
    )

