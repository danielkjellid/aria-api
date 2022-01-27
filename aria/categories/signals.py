from django.db.models.signals import post_delete
from django.dispatch import receiver

from aria.core.utils import cleanup_files_from_deleted_instance
from aria.categories.models import Category


@receiver(post_delete, sender=Category)
def delete_product_files(sender, instance, *args, **kwargs):
    cleanup_files_from_deleted_instance(
        sender=sender, instance=instance, *args, **kwargs
    )
