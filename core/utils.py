import os
from django.core.exceptions import FieldDoesNotExist
from django.utils.text import slugify
from django.db.models import Model, ImageField, FileField
from django.conf import settings

def cleanup_files_from_deleted_instance(sender, instance, *args, **kwargs):
    """
    Function to fire when a model instance is deleted, and we need to cleanup
    dangling associated files - deleting them from the system.

    """
    if instance is None:
        raise AttributeError('No instance sent from signal.')

    thumbnail = None
    image = None
    file = None
    parent_dir = None

    try:
        thumbnail = instance._meta.get_field('thumbnail')
        image = instance._meta.get_field('image')
        file = instance._meta.get_field('file')
    except FieldDoesNotExist:
        pass

    if thumbnail and isinstance(instance._meta.get_field('thumbnail'), ImageField):
        if instance.thumbnail and instance.thumbnail.path:
            parent_dir = os.path.dirname(instance.thumbnail.path)
            instance.thumbnail.delete(save=False)

    if image and isinstance(instance._meta.get_field('image'), ImageField):
        if instance.image and instance.image.path:
            parent_dir = os.path.dirname(instance.image.path)
            instance.image.delete(save=False)

    if file and isinstance(instance._meta.get_field('file'), FileField):
        if instance.file and instance.file.path:
            parent_dir = os.path.dirname(instance.file.path)
            instance.file.delete(save=False)

    # TODO: Delete remote empty dirs from s3 as well
    # Delete empty folders locally
    if settings.DEBUG and parent_dir and os.path.isdir(parent_dir) and len(os.listdir(parent_dir)) == 0:
        os.rmdir(parent_dir)


def get_static_asset_upload_path(instance: "Model", filename: str) -> str:
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

    return f'{path}/{slugify(name)}{extension}'
