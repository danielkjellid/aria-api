from django.db.models import Q

from django_filters import FilterSet, filters

from aria.products.models import Product


class ProductSearchFilter(FilterSet):
    """
    A set of searchable fields for the product model.
    """

    search = filters.CharFilter(method="query_products", label="Search")

    class Meta:
        model = Product
        fields = ["search"]

    def query_products(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value)
            | Q(search_keywords__icontains=value)
            | Q(supplier__name__icontains=value)
            | Q(materials__icontains=value)
        )
