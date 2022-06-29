from typing import Any

from django.db.models.signals import post_delete
from django.dispatch import receiver

from aria.categories.models import Category
from aria.core.utils import cleanup_files_from_deleted_instance


@receiver(post_delete, sender=Category)
def delete_product_files(
    sender: Category,  # pylint: disable=unused-argument
    instance: Category,
    *args: Any,
    **kwargs: Any,
) -> None:
    """
    Delete related static assets upon product deletion.
    """
    cleanup_files_from_deleted_instance(instance=instance)
