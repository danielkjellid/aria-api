from typing import Any

from django.db.models import Model
from django.db.models.signals import post_delete
from django.dispatch import receiver

from aria.categories.models import Category
from aria.core.utils import cleanup_files_from_deleted_instance


@receiver(post_delete, sender=Category)
def delete_product_files(
    sender: Model, instance: Model, *args: Any, **kwargs: Any
) -> None:
    cleanup_files_from_deleted_instance(instance=instance)
