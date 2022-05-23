from aria.core.models import BaseQuerySet
from aria.products.enums import ProductStatus


class KitchenQuerySet(BaseQuerySet):
    def available(self):
        """
        Get kitchens with ProductStats Available.
        """
        return self.filter(status=ProductStatus.AVAILABLE)
