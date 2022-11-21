from typing import Any

from django.db.models import Model
from django.db.models.signals import post_delete
from django.dispatch import receiver

from aria.core.utils import cleanup_files_from_deleted_instance
from aria.kitchens.models import Decor, Kitchen, Plywood


@receiver(post_delete, sender=Kitchen)
@receiver(post_delete, sender=Plywood)
@receiver(post_delete, sender=Decor)
def delete_kitchen_files(
    sender: Model,  # pylint: disable=unused-argument
    instance: Model,
    *args: Any,
    **kwargs: Any,
) -> None:
    """
    Signal that deletes related images when a kitchen is deleted.
    """
    cleanup_files_from_deleted_instance(instance=instance)
