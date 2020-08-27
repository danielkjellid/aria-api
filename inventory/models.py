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

    def upload_content_file_name(instance, filename):
        """
        Return the location of which to upload the file
        """
       
        return os.path.join('categories/%s/' % instance.name.lower(), filename)
    
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
        upload_to='categories',
        help_text=_(
            'Category image, should only be used on top level parents!'
        ),
        blank=True, 
        null=True,

    )
    image_default = ImageSpecField(source='image', processors=[ResizeToFill(375, 375)], format='JPEG', options={'quality': 90})
    image_sm = ImageSpecField(source='image', processors=[ResizeToFill(640, 300)], format='JPEG', options={'quality': 90})
    image_md = ImageSpecField(source='image', processors=[ResizeToFill(768, 366)], format='JPEG', options={'quality': 90})
    image_lg = ImageSpecField(source='image', processors=[ResizeToFill(1024, 480)], format='JPEG', options={'quality': 90})
    image_xl = ImageSpecField(source='image', processors=[ResizeToFill(1280, 600)], format='JPEG', options={'quality': 90})
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