from django.db.models.signals import post_delete
from django.dispatch import receiver

from inventory.models.category import Category

"""
The signal bellow fires when a category is deleted, and cleans up the associated
files, deleting them from the system.
"""
@receiver(post_delete, sender=Category)
def delete_category_image(sender, instance, *args, **kwargs):
    if instance.image:
        instance.image.delete()
