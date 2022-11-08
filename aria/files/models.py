from django.db import models

from django_resized import ResizedImageField

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

    def _generate_image_url(
        self, *, width: int | None = None, height: int | None = None
    ) -> str | None:
        """
        Generate a signed image url with dimensions.
        """
        if self.image and self.image.name:
            return image_generate_signed_url(
                image_name=self.image.name, width=width, height=height
            )

        return None

    @property
    def image_url(self) -> str | None:
        """
        Get the url for the native dimensions of the image.
        """
        return self._generate_image_url()


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

    class Meta:
        abstract = True

    @property
    def image1440x810_url(self) -> str | None:
        """
        Get the url for the 1440x810 version of the image.
        """
        return self._generate_image_url(width=1440, height=810)

    @property
    def image1280x720_url(self) -> str | None:
        """
        Get the url for the 1280x720 version of the image.
        """
        return self._generate_image_url(width=1280, height=720)

    @property
    def image1024x576_url(self) -> str | None:
        """
        Get the url for the 1024x576 version of the image.
        """
        return self._generate_image_url(width=1024, height=576)

    @property
    def image960x540_url(self) -> str | None:
        """
        Get the url for the 960x540 version of the image.
        """
        return self._generate_image_url(width=960, height=540)

    @property
    def image768x432_url(self) -> str | None:
        """
        Get the url for the 768x432 version of the image.
        """
        return self._generate_image_url(width=768, height=432)

    @property
    def image640x360_url(self) -> str | None:
        """
        Get the url for the 640x360 version of the image.
        """
        return self._generate_image_url(width=640, height=360)


class BaseCollectionListImageModel(BaseImageModel):
    """
    Generic model for storing and uploading all version needed for a collection list
    image. To add this to a model, create a subclass with the UPLOAD_FILE_PATH
    attribute specified to the path where the image should be uploaded.

    Convention is media/category/supplier/item_name/file_name.extension. All provided
    path variables should be slugified.
    """

    UPLOAD_PATH: str

    class Meta:
        abstract = True

    @property
    def image960x540_url(self) -> str | None:
        """
        Get the url for the 960x540 version of the image.
        """
        return self._generate_image_url(width=960, height=540)

    @property
    def image576x324_url(self) -> str | None:
        """
        Get the url for the 576x324 version of the image.
        """
        return self._generate_image_url(width=576, height=324)


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

    thumbnail = ResizedImageField(
        "thumbnail",
        upload_to=asset_get_static_upload_path,
        size=[THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT],
        blank=True,
        null=True,
    )

    class Meta:
        abstract = True

    def _generate_image_url(
        self, *, width: int | None = None, height: int | None = None
    ) -> str | None:
        """
        Generate a signed image url with dimensions.
        """
        if self.thumbnail and self.thumbnail.name:
            return image_generate_signed_url(
                image_name=self.thumbnail.name, width=width, height=height
            )

        return None

    @property
    def image_url(self) -> str | None:
        """
        Get the url for the native dimensions of the image.
        """
        return self._generate_image_url()

    @property
    def image80x80_url(self) -> str | None:
        """
        Get the url for the 80x80 version of the image.
        """
        return self._generate_image_url(width=80, height=80)

    @property
    def image380x575_url(self) -> str | None:
        """
        Get the url for the 380x575 version of the image.
        """
        return self._generate_image_url(width=380, height=575)
