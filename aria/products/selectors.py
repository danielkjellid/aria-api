from typing import List, Union

from django.db.models import QuerySet

from aria.products.models import Product, Variant


def get_related_unique_variants(
    *, product: "Product"
) -> Union[QuerySet, List[Variant]]:
    return Variant.objects.filter(product_options__product=product).distinct("pk")
