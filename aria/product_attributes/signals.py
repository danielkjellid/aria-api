from typing import Any

from django.db.models import Model
from django.db.models.signals import post_delete
from django.dispatch import receiver

from aria.files.s3_utils import s3_assets_cleanup
from aria.product_attributes.models import Shape, Variant


@receiver(post_delete, sender=Variant)
@receiver(post_delete, sender=Shape)
def delete_images(
    sender: Model,  # pylint: disable=unused-argument
    instance: Model,
    *args: Any,
    **kwargs: Any,
) -> None:
    """
    Delete static assets belonging to deleted instance.
    """
    print("received signal")
    s3_assets_cleanup(instance=instance)
