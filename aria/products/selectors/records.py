from aria.products.models import Product
from aria.products.records import ProductListRecord
from aria.products.selectors.discounts import product_get_active_discount

#####################
# Records selectors #
#####################


def product_list_record(product: Product) -> ProductListRecord:
    """
    Get the record representation for a list of products. Needs to be
    used with a product preloaded for listing. E.g. with the
    .preload_for_list() queryset manager method.
    """

    discount = product_get_active_discount(product=product)
    return ProductListRecord.from_product(product, discount=discount)
