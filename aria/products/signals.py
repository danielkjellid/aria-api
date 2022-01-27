from django.db.models.signals import m2m_changed, post_delete, pre_delete
from django.dispatch import receiver

from aria.categories.models import Category
from aria.core.utils import cleanup_files_from_deleted_instance
from aria.products.models import (
    Product,
    ProductFile,
    ProductImage,
    ProductOption,
    Variant,
)
from aria.products.services import delete_related_variants


@receiver(m2m_changed, sender=Product.categories.through)
def validate_category_being_added(sender, instance, *args, **kwargs):
    action = kwargs.get("action", None)
    categories_pk_set = kwargs.get("pk_set", None)

    if action == "pre_add":
        categories = Category.objects.filter(id__in=categories_pk_set)
        for category in categories:
            if category.is_primary:
                raise Exception(
                    f"You can not add a primary category to categories. Tried to add {category.name}."
                )


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
