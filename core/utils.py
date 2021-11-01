import os
from django.utils.text import slugify
from django.db.models import Model

def cleanup_files_from_deleted_instance(sender, instance, *args, **kwargs):
    """
    Function to fire when a model instance is deleted, and we need to cleanup
    dangling associated files - deleting them from the system.
    """

    if instance and instance.thumbnail:
        instance.thumbnail.delete()

    if instance and instance.image:
        instance.image.delete()

    if instance and instance.file:
        instance.file.delete()


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