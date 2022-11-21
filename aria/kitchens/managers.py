from typing import TYPE_CHECKING

from aria.core.models import BaseQuerySet
from aria.products.enums import ProductStatus

if TYPE_CHECKING:
    from aria.kitchens import models


class KitchenQuerySet(BaseQuerySet["models.Kitchen"]):
    def available(self) -> BaseQuerySet["models.Kitchen"]:
        """
        Get kitchens with ProductStats Available.
        """
        return self.filter(status=ProductStatus.AVAILABLE)
