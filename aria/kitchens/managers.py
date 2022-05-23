from aria.core.models import BaseQuerySet
from aria.products.enums import ProductStatus


class KitchenQuerySet(BaseQuerySet):
    def available(self):

        return self.filter(status=ProductStatus.AVAILABLE)
