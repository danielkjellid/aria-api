import os
from typing import TYPE_CHECKING, Any

from django.conf import settings
from django.core.exceptions import FieldDoesNotExist
from django.db.models import FileField, ImageField, Model
from django.utils.text import slugify

from django_s3_storage.storage import S3Storage
from imagekit.models import ProcessedImageField

if TYPE_CHECKING:
    from aria.core import models as core_models


def cleanup_files_from_deleted_instance(instance: Model) -> None:
    """
    Function to fire when a model instance is deleted, and we need to cleanup
    dangling associated files - deleting them from the system.

    """
    if instance is None:
        raise AttributeError("No instance sent from signal.")

    def _cleanup_folders(
        parent_dir: str | None = None, storage_key: str | None = None
    ) -> None:
        # Since we use AWS in prod and a normal file structure in the media folder
        # in development, check if debug is active and if parent key is sent in.
        if settings.DEBUG and parent_dir:
            # Check if parent_dir is a folder, and that the folder is empty
            if os.path.isdir(parent_dir) and len(os.listdir(parent_dir)) == 0:
                # If so, delete the folder
                os.rmdir(parent_dir)
        # If we're not in debug, check if storage_key was sent int
        elif storage_key:
            # Assert that the key actually exists
            assert (
                storage_key is not None
            ), "Storage key is none, not able to cleanup remote folder"

            # Create a new storage instance based in s3 bucket
            storage = S3Storage(aws_s3_bucket_name=settings.AWS_S3_BUCKET_NAME)

            # Get the "dir" key of file deleted
            parent_dir_key = storage_key.rsplit("/", 1)[
                0
            ]  # Get everything before last /

            # Check if ket exists
            if storage.exists(parent_dir_key):
                # Extract dirs and files within the key
                dirs, files = storage.listdir(parent_dir_key)

                # If both are empty, delete the folder
                if len(dirs) == 0 and len(files) == 0:
                    storage.delete(parent_dir_key)

    def _cleanup_file(instance: "Model", meta_field: str) -> None:
        instance_field = None
        parent_dir = None
        storage_key = None
        field = None

        # Attempt to get field and field and field properties
        try:
            instance_field = instance._meta.get_field(meta_field)
            field = getattr(instance, meta_field)
        except FieldDoesNotExist:
            pass

        # Check if field meta exists, and that field is type Image, ProcessedImage or File
        if (
            field
            and instance_field
            and isinstance(instance_field, (ImageField, ProcessedImageField, FileField))
        ):
            # Since we use AWS in prod, and normal file structure in development
            # check if path property of instance field exists
            try:
                if field.path:
                    # Find correct parent folder, and delete the file/image
                    parent_dir = os.path.dirname(field.path)
                    field.delete(save=False)
            except NotImplementedError:
                # Get the storage key remote and delete the file/image
                # django_s3_storage handles the remote deletion by
                # overrideing the delete method for us.
                storage_key = field.name
                field.delete(save=False)

            # When the file is deleted, perfor preliminary check on the folder
            # to delete empty folders from the system as well
            _cleanup_folders(parent_dir=parent_dir, storage_key=storage_key)

    _cleanup_file(instance=instance, meta_field="thumbnail")
    _cleanup_file(instance=instance, meta_field="image")
    _cleanup_file(instance=instance, meta_field="file")


def get_static_asset_upload_path(
    instance: "core_models.BaseImageModel", filename: str
) -> str:
    """
    Get the path of which to upload the image.
    """

    # Each image model is required to specify where images should be uploaded
    try:
        path = instance.UPLOAD_PATH.lower()
    except AttributeError:
        raise RuntimeError(
            f"UPLOAD_PATH is not set on model: {instance.__class__.__name__}"
        )

    name, extension = os.path.splitext(filename)

    return f"{path}/{slugify(name)}{extension}"


def get_array_field_labels(
    choices: Any | None, enum: Any
) -> list[dict[str, str] | None]:
    """
    Return a list of human readable labels for ArrayChoiceFields
    """

    if choices is None:
        return []

    return [
        {"name": item.label}
        for item in enum
        for choice in choices
        if item.value == choice and item.label
    ]
