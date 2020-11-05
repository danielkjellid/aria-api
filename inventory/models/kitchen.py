from django.db import models
from django.utils.translation import gettext_lazy as _
from imagekit.models import ImageSpecField, ProcessedImageField
from imagekit.processors import ResizeToFill

from inventory.models.category import SubCategory
from inventory.models.common import Status
from inventory.models.supplier import Supplier

class KitchenSilkColor(models.Model):

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
        verbose_name = _('Kithcen silk color')
        verbose_name_plural = _('Kitchen silks colors')

    def __str__(self):
        return self.name.strip()


class KitchenDecor(models.Model):

    def kitchen_decor_directory_path(self, filename):
        """
        Method to upload the files to the appropriate path
        """

        return 'media/kitchens/decors/{0}/{1}'.format(self.name, filename)

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
        verbose_name = _('Kithcen decor')
        verbose_name_plural = _('Kitchen decors')

    def __str__(self):
        return self.name.strip()


class KitchenPlywood(models.Model):

    def kitchen_plywood_directory_path(self, filename):
        """
        Method to upload the files to the appropriate path
        """

        return 'media/kitchens/plywoods/{0}/{1}'.format(self.name, filename)

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
        verbose_name = _('Kithcen plywood')
        verbose_name_plural = _('Kitchen plywoods')

    def __str__(self):
        return self.name.strip()


class KitchenLaminateColor(models.Model):

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
        verbose_name = _('Kithcen laminate color')
        verbose_name_plural = _('Kitchen laminates colors')

    def __str__(self):
        return self.name.strip()


class KitchenExclusiveColor(models.Model):

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
        verbose_name = _('Kithcen exclusive color')
        verbose_name_plural = _('Kitchen exclusives colors')

    def __str__(self):
        return self.name.strip()


class KitchenTrendColor(models.Model):

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
        verbose_name = _('Kithcen trend color')
        verbose_name_plural = _('Kitchen trend colors')

    def __str__(self):
        return self.name.strip()



class Kitchen(models.Model):

    def kitchen_directory_path(self, filename):
        """
        Method to upload the files to the appropriate path
        """

        return 'media/kitchens/{0}/{1}'.format(self.name, filename)


    name = models.CharField(
        _('Kitchen name'),
        max_length=255,
        unique=True
    )
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        related_name='supplier_kitchen'
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
        KitchenSilkColor,
        related_name='kitchen_silk',
        blank=True
    )
    decor_variants = models.ManyToManyField(
        KitchenDecor,
        related_name='kitchen_decor',
        blank=True
    )
    plywood_variants = models.ManyToManyField(
        KitchenPlywood,
        related_name='kitchen_plywood',
        blank=True
    )
    laminate_variants = models.ManyToManyField(
        KitchenLaminateColor,
        related_name='kitchen_decor',
        blank=True
    )
    exclusive_variants = models.ManyToManyField(
        KitchenExclusiveColor,
        related_name='kitchen_exclusive',
        blank=True
    )
    trend_variants = models.ManyToManyField(
        KitchenTrendColor,
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
    image_1536x1536 = ImageSpecField(
        source='image', 
        processors=[ResizeToFill(1536, 1536)], 
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
