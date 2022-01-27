from django.db.models import F
from aria.products.enums import ProductStatus
from aria.core.models import BaseManager, BaseQuerySet


class ProductManager(BaseManager):
    pass


class ProductQuerySet(BaseQuerySet):
    def preload_for_list(self):
        """
        Utility to avoid 0(n) queries
        """

        return self.prefetch_related("categories", "colors", "shapes")

    def by_category(self, category, ordered: bool = True):
        # Prepare queryset and get active decendants
        categories = category.get_descendants(include_self=True).active()

        products = self.objects.filter(
            status=ProductStatus.AVAILABLE, categories__in=categories
        )

        if ordered:
            products.annotate(
                _ordering=categories.values_list("ordering")[:1]
            ).order_by(F("_ordering").asc(nulls_last=True), "name")
