from django.db import models
from django.utils.translation import gettext_lazy as _


class Category(models.Model):

    class CategoryWidth(models.TextChoices):
        FULL = 'Full', _('Fullwidth')
        HALF = 'Half', _('Half width')

    # model fields
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE, 
        related_name='category',
        null=True,
    )
    order = models.PositiveIntegerField(
        _('order'),
        unique=True,
        help_text=_('Order  in which the category should be displayed')
    )
    name = models.CharField(
        _('category name'),
        max_length=255, 
        unique=True
    )
    width = models.CharField(
        _('width'), 
        max_length=4, 
        choices=CategoryWidth.choices,
        default=CategoryWidth.FULL
    )
    image = models.ImageField(_('image'))
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_('Designates whether the category should be treated as active.'),
    )

    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')
