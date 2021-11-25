from django.dispatch import receiver
from django.db.models.signals import post_delete, pre_delete

from aria.core.utils import cleanup_files_from_deleted_instance

from aria.products.models import (
    Product,
    ProductImage,
    ProductFile,
    Variant,
    ProductOption,
)
from aria.products.services import delete_related_variants


@receiver(post_delete, sender=Product)
@receiver(post_delete, sender=ProductImage)
@receiver(post_delete, sender=ProductFile)
@receiver(post_delete, sender=Variant)
def delete_product_files(sender, instance, *args, **kwargs):
    cleanup_files_from_deleted_instance(
        sender=sender, instance=instance, *args, **kwargs
    )


@receiver(pre_delete, sender=ProductOption)
def delete_related_product_variants(sender, instance, *args, **kwargs):
    delete_related_variants(instance=instance)
