from typing import Any

from django.db.models import Model
from django.db.models.signals import post_delete
from django.dispatch import receiver

from aria.core.utils import cleanup_files_from_deleted_instance
from aria.product_attributes.models import Shape, Variant


@receiver(post_delete, Variant)
@receiver(post_delete, Shape)
def delete_images(
    sender: Model,  # pylint: disable=unused-argument
    instance: Model,
    *args: Any,
    **kwargs: Any,
) -> None:
    """
    Delete static assets belonging to deleted instance.
    """

    cleanup_files_from_deleted_instance(instance=instance)
