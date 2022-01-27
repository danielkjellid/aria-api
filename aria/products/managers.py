from django.db.models import F

from aria.core.models import BaseManager, BaseQuerySet
from aria.products.enums import ProductStatus


class ProductManager(BaseManager):
    pass


class ProductQuerySet(BaseQuerySet):
    def preload_for_list(self):
        """
        Utility to avoid n+1 queries
        """

        return self.prefetch_related("categories", "colors", "shapes")

    def by_category(self, category, ordered: bool = True):
        # Prepare queryset and get active decendants
        categories = category.get_descendants(include_self=True).active()

        print(categories)

        products = self.filter(
            status=ProductStatus.AVAILABLE, categories__in=categories
        )

        if ordered:
            products.annotate(
                _ordering=categories.values_list("ordering")[:1]
            ).order_by(F("_ordering").asc(nulls_last=True), "name")

        return products
