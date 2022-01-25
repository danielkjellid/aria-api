from django_filters import FilterSet, filters

from aria.products.models import Product


class ProductFilter(FilterSet):
    """
    A set of searchable fields for the product model.
    """

    materials = filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = Product
        fields = ("name", "search_keywords", "supplier__name", "materials")
