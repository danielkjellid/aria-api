from django.core.files import File
from django.utils.text import slugify

from products.models import Variant
from products.enums import ProductStatus


def create_variant(
    *,
    name: str,
    status: int = ProductStatus.DRAFT,
    thumbnail: File = None
) -> Variant:
    """
    Creates a Variant with given fields.
    """

    if not name or not status or not thumbnail:
        raise ValueError(
            'Not all fields necessary present. Got name: %s, status: %s, thumbnail: %s - ',
            name,
            status,
            thumbnail
        )

    new_variant = Variant.objects.create(
        name=name.title(),
        status=status
    )

    # Variants needs an id to save files because the folder structure is
    # <id>-<name>/file, therefore we have to create the variant first,
    # then save the thumbnail file.
    new_variant.thumbnail.save(f'{slugify(new_variant.name)}', thumbnail)

    return new_variant
