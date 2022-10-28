from typing import Iterable, TypeVar

from django.db import models
from django.db.models.expressions import Case, When

from imagekit.models import ImageSpecField
from imagekit.models.fields import ProcessedImageField
from imagekit.processors import ResizeToFill

from aria.core.utils import get_static_asset_upload_path
from aria.core.validators import image_validate
from aria.files.thumbor import image_generate_signed_url

T = TypeVar("T", bound=models.Model)


class BaseQuerySet(models.QuerySet[T]):
    def order_by_ids(self, ids: list[int]) -> models.QuerySet[T]:
        """
        Order queryset by a fixed list of ids.
        """
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

    created_at = models.DateTimeField("created time", auto_now_add=True)
    updated_at = models.DateTimeField("modified time", auto_now=True)


class BaseImageModel(models.Model):
    """
    Generic image model. Comes ready with upload path, validation and most used
    dimension properties.
    """

    class Meta:
        abstract = True

    UPLOAD_PATH: str

    image = models.ImageField(
        "Image",
        upload_to=get_static_asset_upload_path,
        blank=True,
        null=False,
    )

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

    @property
    def image576x324_url(self) -> str:
        return image_generate_signed_url(
            image_name=self.image.name, width=1440, height=810
        )


class _BaseHeaderImageModel(BaseImageModel):
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


class BaseHeaderImageModel(BaseImageModel):
    """
    Generic model for storing and uploading all version needed for a header image.
    To add this to a model, create a subclass with the UPLOAD_FILE_PATH
    attribute specified to the path where the image should be uploaded.

    Convention is media/category/supplier/item_name/file_name. All provided
    path variables should be slugified.
    """

    class Meta:
        abstract = True

    UPLOAD_PATH: str

    apply_filter = models.BooleanField(
        "Apply filter",
        default=False,
        help_text=(
            "Apply filter to image if the image is light to "
            "maintain an acceptable contrast"
        ),
    )
    image_512x512 = ImageSpecField(
        source="image",
        processors=[ResizeToFill(512, 512)],
        format="JPEG",
        options={"quality": 90},
    )
    image_640x275 = ImageSpecField(
        source="image",
        processors=[ResizeToFill(640, 275)],
        format="JPEG",
        options={"quality": 90},
    )
    image_1024x1024 = ImageSpecField(
        source="image",
        processors=[ResizeToFill(1024, 1024)],
        format="JPEG",
        options={"quality": 90},
    )
    image_1024x575 = ImageSpecField(
        source="image",
        processors=[ResizeToFill(1024, 575)],
        format="JPEG",
        options={"quality": 90},
    )
    image_1536x860 = ImageSpecField(
        source="image",
        processors=[ResizeToFill(1536, 860)],
        format="JPEG",
        options={"quality": 90},
    )
    image_2048x1150 = ImageSpecField(
        source="image",
        processors=[ResizeToFill(2048, 1150)],
        format="JPEG",
        options={"quality": 90},
    )


class BaseListImageModel(BaseImageModel):
    class Meta:
        abstract = True

    image500x305 = ImageSpecField(
        source="image",
        processors=[ResizeToFill(500, 305)],
        format="JPEG",
        options={"quality": 90},
    )
    image600x440 = ImageSpecField(
        source="image",
        processors=[ResizeToFill(600, 440)],
        format="JPEG",
        options={"quality": 90},
    )
    image850x520 = ImageSpecField(
        source="image",
        processors=[ResizeToFill(850, 520)],
        format="JPEG",
        options={"quality": 90},
    )


class BaseThumbnailImageModel(models.Model):
    class Meta:
        abstract = True

    UPLOAD_PATH: str

    thumbnail = ProcessedImageField(
        upload_to=get_static_asset_upload_path,
        processors=[ResizeToFill(380, 575)],
        format="JPEG",
        options={"quality": 90},
        blank=True,
        null=False,
        help_text="Image must be above 380x575px",
    )


class BaseFileModel(BaseModel):
    class Meta:
        abstract = True

    UPLOAD_PATH: str

    file = models.FileField("File", upload_to=get_static_asset_upload_path)
