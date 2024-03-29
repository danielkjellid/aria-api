from typing import Any

from django.db.models import Model
from django.db.models.signals import m2m_changed, post_delete, pre_delete
from django.dispatch import receiver
from django.utils.translation import gettext as _

from aria.categories.models import Category
from aria.core.exceptions import ApplicationError
from aria.files.s3_utils import s3_assets_cleanup
from aria.products.models import Product, ProductFile, ProductImage, ProductOption
from aria.products.services.product_options import (
    product_option_delete_related_variants,
)


def _validate_category(**kwargs: Any) -> None:
    """
    Validate that products are only added to a child category.
    """

    action = kwargs.get("action", None)
    categories_pk_set = kwargs.get("pk_set", None)

    if action == "pre_add":
        categories = Category.objects.filter(id__in=categories_pk_set)
        for category in categories:
            if category.is_primary:
                raise ApplicationError(
                    message=_(
                        "You can not add a primary category to products. Tried to "  # pylint: disable=C0209, line-too-long
                        "add %s." % category.name
                    )
                )


@receiver(m2m_changed, sender=Product.categories.through)
def validate_category_being_added(
    sender: Model,  # pylint: disable=unused-argument
    instance: Model,  # pylint: disable=unused-argument
    *args: Any,
    **kwargs: Any,
) -> None:
    """
    Validate that products are only added to a child category.
    """

    _validate_category(**kwargs)


@receiver(post_delete, sender=Product)
@receiver(post_delete, sender=ProductImage)
@receiver(post_delete, sender=ProductFile)
def delete_product_files(
    sender: Model,  # pylint: disable=unused-argument
    instance: Model,
    *args: Any,
    **kwargs: Any,
) -> None:
    """
    Delete static assets belonging to deleted instance.
    """

    s3_assets_cleanup(instance=instance)


@receiver(pre_delete, sender=ProductOption)
def delete_related_product_variants(
    sender: ProductOption,  # pylint: disable=unused-argument
    instance: ProductOption,
    *args: Any,
    **kwargs: Any,
) -> None:
    """
    Delete variants that does not bellong to other products.
    """

    product_option_delete_related_variants(instance=instance)
