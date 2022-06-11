from django.core.files import File
from django.utils.text import slugify

from aria.products.models import ProductOption, Variant


def variant_create(*, name: str, thumbnail: File | None = None) -> Variant:
    """
    Creates a Variant with given fields.
    """

    if not name:
        raise ValueError(
            "Not all fields necessary present. Got name: %s, status: %s, thumbnail: %s - ",
            name,
        )

    new_variant = Variant.objects.create(name=name.title())

    # Variants needs an id to save files because the folder structure is
    # <id>-<name>/file, therefore we have to create the variant first,
    # then save the thumbnail file.
    if thumbnail:
        new_variant.thumbnail.save(f"{slugify(new_variant.name)}", thumbnail)

    return new_variant


def product_option_delete_related_variants(*, instance: "ProductOption") -> None:
    """
    Cleanup dangling variants that does not belong to other
    products.
    """

    related_variant: Variant | None = instance.variant

    # Check if there are other products thats linked to the same
    # variant while filtering out standards.
    if (
        related_variant is not None
        and related_variant.is_standard is False
        and len(related_variant.product_options.all()) == 1
    ):
        related_variant.delete()
