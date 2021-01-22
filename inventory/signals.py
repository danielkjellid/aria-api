from django.db.models.signals import post_delete
from django.dispatch import receiver

from inventory.models.product import Product, ProductImage, ProductVariant, ProductFile

@receiver(post_delete, sender=Product)
"""
Receiver to delete images from S3 on model delete
"""
def delete_files(sender, instance, *args, **kwargs):
    if instance.thumbnail:
        instance.thumbnail.delete(save=False)
