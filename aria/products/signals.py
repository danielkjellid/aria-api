from typing import Any

from django.db.models import Model
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
from aria.products.services import product_option_delete_related_variants


def _validate_category(**kwargs: Any) -> None:
    action = kwargs.get("action", None)
    categories_pk_set = kwargs.get("pk_set", None)

    if action == "pre_add":
        categories = Category.objects.filter(id__in=categories_pk_set)
        for category in categories:
            if category.is_primary:
                raise Exception(
                    f"You can not add a primary category to categories. Tried to add {category.name}."
                )


@receiver(m2m_changed, sender=Product.categories.through)
def validate_category_being_added(
    sender: Model, instance: Model, *args: Any, **kwargs: Any
) -> None:
    _validate_category(**kwargs)


@receiver(post_delete, sender=Product)
@receiver(post_delete, sender=ProductImage)
@receiver(post_delete, sender=ProductFile)
@receiver(post_delete, sender=Variant)
def delete_product_files(
    sender: Model, instance: Model, *args: Any, **kwargs: Any
) -> None:
    cleanup_files_from_deleted_instance(instance=instance)


@receiver(pre_delete, sender=ProductOption)
def delete_related_product_variants(
    sender: ProductOption, instance: ProductOption, *args: Any, **kwargs: Any
) -> None:
    product_option_delete_related_variants(instance=instance)
