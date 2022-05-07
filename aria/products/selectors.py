from typing import List, Union

from django.db.models import QuerySet

from aria.categories.models import Category
from aria.products.enums import ProductStatus
from aria.products.filters import ProductSearchFilter
from aria.products.models import Product, Variant


def get_related_unique_variants(
    *, product: "Product"
) -> Union[QuerySet, List[Variant]]:
    return Variant.objects.filter(product_options__product=product).distinct("pk")


def product_list_by_category(
    *, filters=None, category: Category
) -> Union[QuerySet, Product]:
    """
    Returns a list of products bellonging to the given
    category parent slug.
    """

    filters = filters or {}

    qs = category.get_products().filter(status=ProductStatus.AVAILABLE)

    return ProductSearchFilter(filters, qs).qs
