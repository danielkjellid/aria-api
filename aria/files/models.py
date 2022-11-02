from typing import Iterable

from django.db import models

from aria.core.models import BaseModel
from aria.files.utils import (
    asset_get_static_upload_path,
    image_generate_signed_url,
    image_resize,
)
from aria.files.validators import image_validate


class BaseFileModel(BaseModel):
    """
    Generic file model. Comes ready with upload path validation.
    """

    UPLOAD_PATH: str

    file = models.FileField("File", upload_to=asset_get_static_upload_path)

    class Meta:
        abstract = True


class BaseImageModel(BaseModel):
    """
    Generic image model. Comes ready with upload path and image validation.
    """

    UPLOAD_PATH: str

    image = models.ImageField(
        "Image",
        upload_to=asset_get_static_upload_path,
        blank=True,
        null=False,
    )

    class Meta:
        abstract = True

    @property
    def image_url(self) -> str:
        return image_generate_signed_url(image_name=self.image.name)

    def save(
        self,
        force_insert: bool = False,
        force_update: bool = False,
        using: str | None = None,
        update_fields: Iterable[str] | None = None,
    ) -> None:
        """
        Validate images on save.
        """

        image_validate(
            image=self.image,
            allowed_extensions=[".jpg", ".jpeg"],
            width_min_px=1440,
            width_max_px=2048,
            height_min_px=810,
            height_max_px=1150,
        )

        super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
        )


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
    def image1440x810_url(self) -> str:
        return image_generate_signed_url(
            image_name=self.image.name, width=1440, height=810
        )

    @property
    def image1280x720_url(self) -> str:
        return image_generate_signed_url(
            image_name=self.image.name, width=1280, height=720
        )

    @property
    def image1024x576_url(self) -> str:
        return image_generate_signed_url(
            image_name=self.image.name, width=1024, height=576
        )

    @property
    def image960x540_url(self) -> str:
        return image_generate_signed_url(
            image_name=self.image.name, width=960, height=540
        )

    @property
    def image768x432_url(self) -> str:
        return image_generate_signed_url(
            image_name=self.image.name, width=768, height=432
        )

    @property
    def image640x360_url(self) -> str:
        return image_generate_signed_url(
            image_name=self.image.name, width=640, height=360
        )


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
    def image960x540_url(self) -> str:
        return image_generate_signed_url(
            image_name=self.image.name, width=960, height=540
        )

    @property
    def image576x324_url(self) -> str:
        return image_generate_signed_url(
            image_name=self.image.name, width=576, height=324
        )


class BaseThumbnailImage(BaseImageModel):
    """
    Generic model for storing and uploading all version needed for a thumbnail
    image. To add this to a model, create a subclass with the UPLOAD_FILE_PATH
    attribute specified to the path where the image should be uploaded.

    Convention is media/category/supplier/item_name/file_name.extension. All provided
    path variables should be slugified.

    This base model will also resize the uploaded image before saving.
    """

    UPLOAD_PATH: str

    THUMBNAIL_WIDTH = 350
    THUMBNAIL_HEIGHT = 575

    class Meta:
        abstract = True

    @property
    def image80x80_url(self) -> str:
        return image_generate_signed_url(
            image_name=self.image.name, width=80, height=80
        )

    @property
    def image380x575_url(self) -> str:
        return image_generate_signed_url(
            image_name=self.image.name, width=380, height=575
        )

    def save(
        self,
        force_insert: bool = False,
        force_update: bool = False,
        using: str | None = None,
        update_fields: Iterable[str] | None = None,
    ) -> None:
        """
        Resize and validate image on save.
        """

        image_resize(
            image=self.image,
            max_width=self.THUMBNAIL_WIDTH,
            max_height=self.THUMBNAIL_HEIGHT,
        )

        super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
        )
