from typing import List, Union

from django.db.models import QuerySet
from aria.products.enums import ProductStatus

from aria.products.filters import ProductFilter
from aria.products.models import Product, Variant


def get_related_unique_variants(
    *, product: "Product"
) -> Union[QuerySet, List[Variant]]:
    return Variant.objects.filter(product_options__product=product).distinct("pk")


def product_list(*, filters=None) -> Union[QuerySet, Product]:
    """ """

    filters = filters or {}

    qs = Product.objects.all()

    return ProductFilter(filters, qs).qs


def product_list_by_category(
    *, filters=None, category_slug: str
) -> Union[QuerySet, Product]:
    """
    Returns a list of products bellonging to the given
    category parent slug.
    """

    filters = filters or {}

    qs = (
        Product.objects.all()
        .prefetch_related("category__parent")
        .filter(category__parent__slug=category_slug)
        .distinct("pk")
    )

    return ProductFilter(filters, qs).qs
