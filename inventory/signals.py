from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from inventory.models.product import Product

@receiver(post_delete, sender=Product)
def delete_files(sender, instance, *args, **kwargs):
    if instance.thumbnail:
        instance.thumbnail.delete(save=False)