from typing import TYPE_CHECKING

from aria.core.models import BaseQuerySet
from aria.products.enums import ProductStatus
from aria.products.models import Product

if TYPE_CHECKING:
    from aria.discounts.models import DiscountProduct


class DiscountProductQuerySet(BaseQuerySet):
    def with_products(self) -> BaseQuerySet["DiscountProduct"]:
        """
        Prefetch products related to a discount product. Sets the
        prefetched values attribute as "discounted_products"
        """

        products_for_sale = Product.objects.filter(status=ProductStatus.AVAILABLE)

        return self.prefetch_related(
            "products", queryset=products_for_sale, to_attr="discounted_products"
        )
