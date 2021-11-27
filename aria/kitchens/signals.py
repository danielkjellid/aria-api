from django.db.models.signals import post_delete
from django.dispatch import receiver

from aria.core.utils import cleanup_files_from_deleted_instance
from aria.kitchens.models import Kitchen, Decor, Plywood


@receiver(post_delete, sender=Kitchen)
@receiver(post_delete, sender=Plywood)
@receiver(post_delete, sender=Decor)
def delete_kitchen_files(sender, instance, *args, **kwargs):
    cleanup_files_from_deleted_instance(instance=instance)
