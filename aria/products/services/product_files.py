from django.core.files.uploadedfile import InMemoryUploadedFile, UploadedFile

from aria.products.models import Product, ProductFile
from aria.products.records import ProductFileRecord


def product_file_create(
    *, product: Product, name: str, file: UploadedFile | InMemoryUploadedFile
) -> ProductFileRecord:
    """
    Create a product file associated to a product.
    """

    product_file = ProductFile.objects.create(product=product, name=name, file=file)

    return ProductFileRecord(
        id=product_file.id,
        product_id=product_file.product.id,
        name=product_file.name,
        file=product_file.file.url if product_file.file.url else None,
    )
