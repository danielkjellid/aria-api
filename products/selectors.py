from typing import Union, List
from django.db.models import QuerySet
from products.models import Product, Variant

def get_related_unique_variants(*, product: "Product") -> Union[QuerySet, List[Variant]]:
    return Variant.objects.filter(product_options__product=product).distinct('pk')
