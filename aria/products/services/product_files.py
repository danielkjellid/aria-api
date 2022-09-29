from django.core.files import File

from aria.products.models import Product, ProductFile
from django.core.files import File

from aria.products.models import Product, ProductFile


def product_file_create(*, product: Product, name: str, file: File) -> ProductFile:
    """
    Create a product file associated to a product.
    """
    return ProductFile.objects.create(product=product, name=name, file=file)
