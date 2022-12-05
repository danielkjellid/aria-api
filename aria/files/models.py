from django.db import models

from django_resized import ResizedImageField
from imagekit.models import ImageSpecField
from imagekit.models.fields import ProcessedImageField
from imagekit.processors import ResizeToFill

from aria.files.utils import asset_get_static_upload_path, image_generate_signed_url


class BaseFileModel(models.Model):
    """
    Generic file model. Comes ready with upload path validation.
    """

    UPLOAD_PATH: str

    file = models.FileField("File", upload_to=asset_get_static_upload_path)

    class Meta:
        abstract = True


class BaseImageModel(models.Model):
    """
    Generic image model. Comes ready with upload path and image validation.
    """

    UPLOAD_PATH: str

    image = models.ImageField(
        "Image",
        upload_to=asset_get_static_upload_path,
        blank=True,
        null=True,
    )

    class Meta:
        abstract = True

    @staticmethod
    def _get_image_url(field: models.ImageField | ImageSpecField) -> str | None:
        """
        Get url of image variant with safeguard.
        """
        if field and hasattr(field, "url"):
            return field.url

        return None

    @property
    def image_url(self) -> str | None:
        """
        Get the url for the native dimensions of the image.
        """
        return self._get_image_url(field=self.image)


class BaseHeaderImageModel(BaseImageModel):
    """
    Generic model for storing and uploading all version needed for a header image.
    To add this to a model, create a subclass with the UPLOAD_FILE_PATH
    attribute specified to the path where the image should be uploaded.

    Convention is media/category/supplier/item_name/file_name.extension. All provided
    path variables should be slugified.
    """

    UPLOAD_PATH: str

    # Validation of one main image per related set needs to be implemented on a
    # model-to-model basis.
    is_main_image = models.BooleanField(
        "Is main image",
        default=False,
        help_text=(
            "The image we display first in a series of related images. Should only "
            "apply to one of the images in relation."
        ),
    )
    apply_filter = models.BooleanField(
        "Apply filter",
        default=False,
        help_text=(
            "Apply filter to image if the image is light to "
            "maintain an acceptable contrast"
        ),
    )
    image1920x1080 = ImageSpecField(
        source="image",
        processors=[ResizeToFill(1920, 1080)],
        format="WEBP",
        options={"quality": 95},
    )
    image1440x810 = ImageSpecField(
        source="image",
        processors=[ResizeToFill(1440, 810)],
        format="WEBP",
        options={"quality": 95},
    )
    image1280x720 = ImageSpecField(
        source="image",
        processors=[ResizeToFill(1280, 720)],
        format="WEBP",
        options={"quality": 95},
    )
    image1024x576 = ImageSpecField(
        source="image",
        processors=[ResizeToFill(1024, 576)],
        format="WEBP",
        options={"quality": 95},
    )
    image960x540 = ImageSpecField(
        source="image",
        processors=[ResizeToFill(960, 540)],
        format="WEBP",
        options={"quality": 95},
    )
    image768x432 = ImageSpecField(
        source="image",
        processors=[ResizeToFill(768, 432)],
        format="WEBP",
        options={"quality": 95},
    )
    image640x360 = ImageSpecField(
        source="image",
        processors=[ResizeToFill(640, 360)],
        format="WEBP",
        options={"quality": 95},
    )

    class Meta:
        abstract = True

    @property
    def image1920x1080_url(self) -> str | None:
        """
        Get the url for the 1920x1080 version of the image.
        """
        return self._get_image_url(field=self.image1920x1080)

    @property
    def image1440x810_url(self) -> str | None:
        """
        Get the url for the 1440x810 version of the image.
        """
        return self._get_image_url(field=self.image1440x810)

    @property
    def image1280x720_url(self) -> str | None:
        """
        Get the url for the 1280x720 version of the image.
        """
        return self._get_image_url(field=self.image1280x720)

    @property
    def image1024x576_url(self) -> str | None:
        """
        Get the url for the 1024x576 version of the image.
        """
        return self._get_image_url(field=self.image1024x576)

    @property
    def image960x540_url(self) -> str | None:
        """
        Get the url for the 960x540 version of the image.
        """
        return self._get_image_url(field=self.image960x540)

    @property
    def image768x432_url(self) -> str | None:
        """
        Get the url for the 768x432 version of the image.
        """
        return self._get_image_url(field=self.image768x432)

    @property
    def image640x360_url(self) -> str | None:
        """
        Get the url for the 640x360 version of the image.
        """
        return self._get_image_url(field=self.image640x360)


class BaseCollectionListImageModel(BaseImageModel):
    """
    Generic model for storing and uploading all version needed for a collection list
    image. To add this to a model, create a subclass with the UPLOAD_FILE_PATH
    attribute specified to the path where the image should be uploaded.

    Convention is media/category/supplier/item_name/file_name.extension. All provided
    path variables should be slugified.
    """

    UPLOAD_PATH: str

    image960x540 = ImageSpecField(
        source="image",
        processors=[ResizeToFill(960, 540)],
        format="WEBP",
        options={"quality": 95},
    )

    image576x324 = ImageSpecField(
        source="image",
        processors=[ResizeToFill(960, 540)],
        format="WEBP",
        options={"quality": 95},
    )

    class Meta:
        abstract = True

    @property
    def image960x540_url(self) -> str | None:
        """
        Get the url for the 960x540 version of the image.
        """
        return self._get_image_url(field=self.image960x540)

    @property
    def image576x324_url(self) -> str | None:
        """
        Get the url for the 576x324 version of the image.
        """
        return self._get_image_url(field=self.image576x324)


class BaseThumbnailImageModel(models.Model):
    """
    Generic model for storing and uploading all version needed for a thumbnail
    image. To add this to a model, create a subclass with the UPLOAD_FILE_PATH
    attribute specified to the path where the image should be uploaded.

    Convention is media/category/supplier/item_name/file_name.extension. All provided
    path variables should be slugified.

    This base model will also resize the uploaded image before saving.
    """

    UPLOAD_PATH: str

    THUMBNAIL_WIDTH = 380
    THUMBNAIL_HEIGHT = 575

    thumbnail = models.ImageField(
        "Thumbnail",
        upload_to=asset_get_static_upload_path,
        blank=True,
        null=True,
    )

    thumbnail80x80 = ImageSpecField(
        source="thumbnail",
        processors=[ResizeToFill(80, 80)],
        format="WEBP",
        options={"quality": 95},
    )

    thumbnail380x575 = ImageSpecField(
        source="thumbnail",
        processors=[ResizeToFill(380, 575)],
        format="WEBP",
        options={"quality": 95},
    )

    class Meta:
        abstract = True

    @staticmethod
    def _get_image_url(field: models.ImageField | ImageSpecField) -> str | None:
        """
        Get url of image variant with safeguard.
        """
        if field and hasattr(field, "url"):
            return field.url

        return None

    @property
    def image_url(self) -> str | None:
        """
        Get the url for the native dimensions of the image.
        """
        return self._get_image_url(field=self.thumbnail)

    @property
    def image80x80_url(self) -> str | None:
        """
        Get the url for the 80x80 version of the image.
        """
        return self._get_image_url(field=self.thumbnail80x80)

    @property
    def image380x575_url(self) -> str | None:
        """
        Get the url for the 380x575 version of the image.
        """
        return self._get_image_url(field=self.thumbnail380x575)
