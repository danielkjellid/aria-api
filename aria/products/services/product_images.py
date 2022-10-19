import os

from django.core.files.images import ImageFile, get_image_dimensions
from django.core.files.uploadedfile import InMemoryUploadedFile, UploadedFile
from django.utils.translation import gettext as _

from aria.core.exceptions import ApplicationError
from aria.products.models import Product, ProductImage
from aria.products.records import ProductImageRecord


def _validate_product_image(
    *, image: UploadedFile | InMemoryUploadedFile | ImageFile
) -> None:
    """
    Validate an images aspect ratio and file type.
    """

    file_extension = None
    allowed_image_types = [".jpg", ".jpeg"]
    width, height = get_image_dimensions(image)

    if image.name is not None:
        _file_name, file_extension = os.path.splitext(image.name)

    if file_extension is not None and file_extension not in allowed_image_types:
        raise ApplicationError(
            message=_("Image does not have a valid type. We only allow jpg/jpeg types.")
        )

    if width is not None and width < 1536:
        raise ApplicationError(message=_("Images should be at least 1536px wide."))

    if height is not None and height < 860:
        raise ApplicationError(message=_("Images should be at least 860px high."))


def product_image_create(
    *,
    product: Product,
    image: UploadedFile | InMemoryUploadedFile | ImageFile,
    apply_filter: bool = False,
) -> ProductImageRecord:
    """
    Create a product image associated to a product.
    """

    _validate_product_image(image=image)

    product_image = ProductImage.objects.create(
        product=product, image=image, apply_filter=apply_filter
    )

    return ProductImageRecord(
        id=product_image.id,
        product_id=product_image.product_id,
        image_url=product_image.image.url if product_image.image else None,
    )
