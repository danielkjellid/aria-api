from django.dispatch import receiver
from django.db.models.signals import post_delete

from core.utils import cleanup_files_from_deleted_instance

from products.models import Product, ProductImage, ProductVariant, ProductFile

@receiver(post_delete, sender=Product)
@receiver(post_delete, sender=ProductImage)
@receiver(post_delete, sender=ProductVariant)
@receiver(post_delete, sender=ProductFile)
def delete_product_files(sender, instance, *args, **kwargs):
    cleanup_files_from_deleted_instance(sender=sender, instance=instance, *args, **kwargs)

