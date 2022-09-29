from django.core.files import File
from django.db import transaction
from django.utils.text import slugify

from aria.products.models import Variant


@transaction.atomic
def variant_create(
    *,
    name: str,
    thumbnail: File | None = None,  # type: ignore
    is_standard: bool = False,
) -> Variant:
    """
    Creates a Variant with given fields.
    """

    assert name, "Name is required to create a variant."

    new_variant = Variant.objects.create(name=name.title(), is_standard=is_standard)

    # Variants needs an id to save files because the folder structure is
    # <id>-<name>/file, therefore we have to create the variant first,
    # then save the thumbnail file.
    if thumbnail:
        new_variant.thumbnail.save(f"{slugify(new_variant.name)}", thumbnail)

    return new_variant
