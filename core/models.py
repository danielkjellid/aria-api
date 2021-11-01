import os
from django.db import models
from django.utils.text import slugify
from django.db.models.expressions import Case, When
from django.utils.translation import gettext_lazy as _
from imagekit.models import ImageSpecField
from imagekit.models.fields import ProcessedImageField
from imagekit.processors import ResizeToFill
from core.utils import get_static_asset_upload_path


class BaseManager(models.Manager):
    pass


class BaseQuerySet(models.QuerySet):
    def order_by_ids(self, ids): #TODO: add type annotation
        if not ids:
            return self
        
        preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(ids)])
        return self.order_by(preserved)


class BaseModel(models.Model):
    """
    Keep track of created time and modified time in models.
    """

    class Meta:
        abstract = True

    created_at = models.DateTimeField(_('created time'), auto_now_add=True)
    updated_at = models.DateTimeField(_('modified time'), auto_now=True)

    object = BaseManager.from_queryset(BaseQuerySet)()


class BaseImageModel(models.Model):
    """
    Generic image model, usually inherited by models with
    specified ImageKit fields.
    """

    class Meta:
        abstract = True

    UPLOAD_PATH: str
    
    image = models.ImageField(
        _('Image'),
        upload_to=get_static_asset_upload_path,
        blank=True, 
        null=True,
    )


class BaseHeaderImageModel(BaseImageModel):

    class Meta:
        abstract = True

    """
    Generic model for storing and uploading all version needed for an header image.
    To add this to a model, create a subclass with the UPLOAD_FILE_PATH 
    attribute specified to the path where the image should be uploaded.

    Convention is media/category/supplier/item_name/file_name. All provided
    path variables should be slugified.
    """

    UPLOAD_PATH: str

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


class BaseThumbnailImageModel(models.Model):
    
    class Meta:
        abstract = True

    UPLOAD_PATH: str

    # Options for setting height/width, with defaults
    WIDTH: int = 380 
    HEIGHT: int = 575

    thumbnail = ProcessedImageField(
        upload_to=get_static_asset_upload_path,
        processors=[ResizeToFill(WIDTH, HEIGHT)],
        format='JPEG',
        options={'quality': 90},
        blank=True,
        null=True,
        help_text=(
            f'Image must be above {WIDTH}x{HEIGHT}px'
        )
    )    


class BaseFileModel(BaseModel):

    class Meta:
        abstract = True

    UPLOAD_PATH: str

    file = models.FileField(
        _('File'), 
        upload_to=get_static_asset_upload_path
    )
