from typing import TYPE_CHECKING

from django.db.models import F, Q
from django.utils import timezone

from aria.core.managers import BaseQuerySet

if TYPE_CHECKING:
    from aria.discounts import models


class DiscountQuerySet(BaseQuerySet["models.Discount"]):
    def active(self) -> BaseQuerySet["models.Discount"]:
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
