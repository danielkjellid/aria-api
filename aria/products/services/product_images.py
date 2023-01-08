from django.core.files.images import ImageFile
from django.core.files.uploadedfile import InMemoryUploadedFile, UploadedFile

from aria.files.validators import image_validate
from aria.products.models import Product, ProductImage
from aria.products.records import ProductImageRecord


def product_image_create(
    *,
    product: Product,
    image: UploadedFile | InMemoryUploadedFile | ImageFile,
    apply_filter: bool | None,
    is_main_image: bool | None,
) -> ProductImageRecord:
    """
    Create a product image associated to a product.
    """

    image_validate(
        image=image,
        allowed_extensions=[".jpg", ".jpeg"],
        width_min_px=1536,
        width_max_px=2048,
        height_min_px=860,
        height_max_px=1500,
    )

    product_image = ProductImage.objects.create(
        product=product,
        image=image,
        apply_filter=apply_filter or False,
        is_main_image=is_main_image or False,
    )

    return ProductImageRecord(
        id=product_image.id,
        product_id=product_image.product_id,
        image_url=product_image.image_url,
    )
