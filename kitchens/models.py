from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from imagekit.models import ImageSpecField, ProcessedImageField
from imagekit.processors import ResizeToFill

from inventory.models.category import SubCategory
from inventory.models.common import Status
from suppliers.models import Supplier

class SilkColor(models.Model):

    name = models.CharField(
        _('Kitchen silk name'),
        max_length=255,
        unique=False
    )
    color_hex = models.CharField(
        _('Color code'),
        max_length=7,
        unique=True
    )

    class Meta:
        verbose_name = _('Silk color')
        verbose_name_plural = _('Silk colors')

    def __str__(self):
        return self.name.strip()


class Decor(models.Model):

    def kitchen_decor_directory_path(self, filename):
        """
        Method to upload the files to the appropriate path
        """

        return 'media/kitchens/decors/{0}/{1}'.format(slugify(self.name), filename)

    name = models.CharField(
        _('Kitchen decor name'),
        max_length=255,
        unique=False
    )
    image = ProcessedImageField(
        upload_to=kitchen_decor_directory_path,
        processors=[ResizeToFill(80, 80)],
        format='JPEG',
        options={'quality': 90},
    )

    class Meta:
        verbose_name = _('Decor')
        verbose_name_plural = _('Decors')

    def __str__(self):
        return self.name.strip()


class Plywood(models.Model):

    def kitchen_plywood_directory_path(self, filename):
        """
        Method to upload the files to the appropriate path
        """

        return 'media/kitchens/plywoods/{0}/{1}'.format(slugify(self.name), filename)

    name = models.CharField(
        _('Kitchen decor name'),
        max_length=255,
        unique=False
    )
    image = ProcessedImageField(
        upload_to=kitchen_plywood_directory_path,
        processors=[ResizeToFill(80, 80)],
        format='JPEG',
        options={'quality': 90},
    )

    class Meta:
        verbose_name = _('Plywood')
        verbose_name_plural = _('Plywoods')

    def __str__(self):
        return self.name.strip()


class LaminateColor(models.Model):

    name = models.CharField(
        _('Kitchen laminate name'),
        max_length=255,
        unique=False
    )
    color_hex = models.CharField(
        _('Color code'),
        max_length=7,
        unique=True
    )

    class Meta:
        verbose_name = _('Laminate color')
        verbose_name_plural = _('Laminates colors')

    def __str__(self):
        return self.name.strip()


class ExclusiveColor(models.Model):

    name = models.CharField(
        _('Kitchen exclusive name'),
        max_length=255,
        unique=False
    )
    color_hex = models.CharField(
        _('Color code'),
        max_length=7,
        unique=True
    )

    class Meta:
        verbose_name = _('Exclusive color')
        verbose_name_plural = _('Exclusive colors')

    def __str__(self):
        return self.name.strip()


class TrendColor(models.Model):

    name = models.CharField(
        _('Kitchen trend name'),
        max_length=255,
        unique=False
    )
    color_hex = models.CharField(
        _('Color code'),
        max_length=7,
        unique=True
    )

    class Meta:
        verbose_name = _('Trend color')
        verbose_name_plural = _('Trend colors')

    def __str__(self):
        return self.name.strip()



class Kitchen(models.Model):

    def kitchen_directory_path(self, filename):
        """
        Method to upload the files to the appropriate path
        """

        return 'media/kitchens/{0}/{1}'.format(slugify(self.name), filename)


    name = models.CharField(
        _('Kitchen name'),
        max_length=255,
        unique=True
    )
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        related_name='supplier'
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
    thumbnail_description = models.CharField(
        _('Thumbnail description'),
        max_length=255,
        unique=False,
    )
    description = models.TextField(_('Description'))
    extra_description = models.TextField(
        _('Extra description'),
        help_text=(
            _('Will be displayed bellow pricing example')
        ),
        blank=True,
        null=True,
    )
    example_from_price = models.FloatField(
        _('From price'),
        blank=True,
        null=True
    )
    can_be_painted = models.BooleanField(
        _('Can be painted'),
        default=False,
        help_text=_(
            'Designates whether the product can be painted in suppliers 2000 colors'
        ),
    )
    silk_variants = models.ManyToManyField(
        SilkColor,
        related_name='kitchen_silk',
        blank=True
    )
    decor_variants = models.ManyToManyField(
        Decor,
        related_name='kitchen_decor',
        blank=True
    )
    plywood_variants = models.ManyToManyField(
        Plywood,
        related_name='kitchen_plywood',
        blank=True
    )
    laminate_variants = models.ManyToManyField(
        LaminateColor,
        related_name='kitchen_decor',
        blank=True
    )
    exclusive_variants = models.ManyToManyField(
        ExclusiveColor,
        related_name='kitchen_exclusive',
        blank=True
    )
    trend_variants = models.ManyToManyField(
        TrendColor,
        related_name='kitchen_decor',
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
    apply_filter = models.BooleanField(
        _('Apply filter'),
        default=False,
        help_text=_(
            'Apply filter to image if the image is light to maintain an acceptable contrast'
        ),
    )
    image = models.ImageField(
        _('Image'),
        help_text=(
            _('Image must be above 3072x940px')
        ),
        upload_to=kitchen_directory_path,
        blank=True,
        null=True
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
    thumbnail_500x305 = ImageSpecField(
        source='image',
        processors=[ResizeToFill(500, 305)],
        format='JPEG', 
        options={'quality': 90}
    )
    thumbnail_660x400 = ImageSpecField(
        source='image',
        processors=[ResizeToFill(660, 400)],
        format='JPEG', 
        options={'quality': 90}
    )
    thumbnail_850x520 = ImageSpecField(
        source='image',
        processors=[ResizeToFill(850, 520)],
        format='JPEG', 
        options={'quality': 90}
    )

    class Meta:
        verbose_name = _('Kitchen')
        verbose_name_plural = _('Kitchens')

    def __str__(self):
        return self.name.strip()
