from typing import TYPE_CHECKING

from django.db.models import F, Prefetch, Q
from django.utils import timezone

from aria.core.models import BaseQuerySet
from aria.products.enums import ProductStatus
from aria.products.models import Product

if TYPE_CHECKING:
    pass


class DiscountQuerySet(BaseQuerySet):
    def active(self) -> BaseQuerySet["Discount"]:
        """
        Return a list of currently active discounts.
        """
        datetime_now = timezone.now()

        return self.filter(
            # Discounts can optionally have a start and/or end time set.
            Q(active_at__isnull=True) | Q(active_at__lte=datetime_now),
            Q(active_to__isnull=True) | Q(active_to__gte=datetime_now),
            # If the discount has a maximum sold quantity set, filter out those
            # discounts that have passed the limit.
            Q(maximum_sold_quantity__isnull=True)
            | Q(maximum_sold_quantity__gt=F("total_sold_quantity")),
        )

    def with_products(self) -> BaseQuerySet["Discount"]:
        """
        Prefetch products related to a discount product. Sets the
        prefetched values attribute as "discounted_products"
        """

        products_for_sale = Product.objects.filter(status=ProductStatus.AVAILABLE)

        prefetched_products = Prefetch(
            "products", queryset=products_for_sale, to_attr="discounted_products"
        )

        return self.prefetch_related(prefetched_products)
