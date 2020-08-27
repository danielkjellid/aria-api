import os
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class Category(models.Model):

    class CategoryWidth(models.TextChoices):
        FULL = 'Full', _('Fullwidth')
        HALF = 'Half', _('Half')

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
        upload_to=upload_content_file_name,
        help_text=_(
            'Category image, should only be used on top level parents!'
        ),
        blank=True, 
        null=True,

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