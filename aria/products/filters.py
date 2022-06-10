from typing import Any

from django.db.models import Q

from django_filters import FilterSet, filters

from aria.core.models import BaseQuerySet
from aria.products.models import Product


class ProductSearchFilter(FilterSet):
    """
    A set of searchable fields for the product model.
    """

    search = filters.CharFilter(method="query_products", label="Search")

    class Meta:
        model = Product
        fields = ["search"]

    @staticmethod
    def query_products(
        queryset: BaseQuerySet[Product], name: Any, value: Any
    ) -> BaseQuerySet[Product]:
        qs: BaseQuerySet[Product] = queryset.filter(
            Q(name__icontains=value)
            | Q(search_keywords__icontains=value)
            | Q(supplier__name__icontains=value)
            | Q(materials__icontains=value)
        )
        return qs
