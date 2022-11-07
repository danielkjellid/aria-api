from decimal import Decimal

from django.core.files.images import ImageFile
from django.core.files.uploadedfile import InMemoryUploadedFile, UploadedFile
from django.utils.text import slugify

from aria.files.validators import image_validate
from aria.product_attributes.models import Size, Variant
from aria.product_attributes.records import (
    SizeDetailRecord,
    SizeRecord,
    VariantDetailRecord,
)
from aria.product_attributes.selectors import size_list_from_mapped_values
from aria.product_attributes.utils import (
    size_clean_and_validate_value,
    size_clean_and_validate_values,
)

#################
# Size services #
#################


def size_create(
    *,
    width: Decimal | float | None = None,
    height: Decimal | float | None = None,
    depth: Decimal | float | None = None,
    circumference: Decimal | float | None = None,
) -> SizeDetailRecord:
    """
    Create a single size instance.
    """

    cleaned_size = size_clean_and_validate_value(
        width=width, height=height, depth=depth, circumference=circumference
    )

    size = Size(
        width=cleaned_size.width,
        height=cleaned_size.height,
        depth=cleaned_size.depth,
        circumference=cleaned_size.circumference,
    )
    size.full_clean()
    size.save()

    return SizeDetailRecord(
        id=size.id,
        name=size.name,
        width=size.width,
        height=size.height,
        depth=size.depth,
        circumference=size.circumference,
    )


def size_bulk_create(*, sizes: list[SizeRecord]) -> list[SizeDetailRecord]:
    """
    Create sizes in bulk based in passed list of dicts, filters out sizes that
    already exists and creates the rest effectively.
    """

    cleaned_sizes = size_clean_and_validate_values(sizes=sizes)
    existing_sizes = Size.objects.all().values(
        "width", "height", "depth", "circumference"
    )

    # Convert dicts to hashable tuples in order to check set differences.
    existing_sizes_tuples = {tuple(size.items()) for size in existing_sizes}
    cleaned_sizes_tuples = {tuple(size.dict().items()) for size in cleaned_sizes}

    # Convert unique tuples back dict and then back to records.
    cleaned_sizes_without_duplicates = [
        SizeRecord(**dict(t))
        for t in cleaned_sizes_tuples.difference(existing_sizes_tuples)
    ]

    sizes_to_create = [
        Size(
            width=size.width,
            height=size.height,
            depth=size.depth,
            circumference=size.circumference,
        )
        for size in cleaned_sizes_without_duplicates
    ]

    Size.objects.bulk_create(sizes_to_create, ignore_conflicts=True)

    # Since we ignore conflicts, not all values passed in are necessarily created.
    # Therefore, we re-fetch all relevant objects and return them instead of the
    # Django's default "all objects that has been created".
    fetched_sizes = size_list_from_mapped_values(values=cleaned_sizes)

    return [
        SizeDetailRecord(
            id=size.id,
            name=size.name,
            width=size.width,
            height=size.height,
            depth=size.depth,
            circumference=size.circumference,
        )
        for size in fetched_sizes
    ]


def size_get_or_create(
    *,
    width: Decimal | float | None,
    height: Decimal | float | None,
    depth: Decimal | float | None,
    circumference: Decimal | float | None,
) -> SizeDetailRecord | None:
    """
    Creates a Size with given fields, if size does not already exist.
    """

    cleaned_size = size_clean_and_validate_value(
        width=width, height=height, depth=depth, circumference=circumference
    )

    if cleaned_size is None:
        return None

    try:
        size = Size.objects.get(
            width=cleaned_size.width,
            height=cleaned_size.height,
            depth=cleaned_size.depth,
            circumference=cleaned_size.circumference,
        )
    except Size.DoesNotExist:
        size = size_create(  # type: ignore
            width=width, height=height, depth=depth, circumference=circumference
        )

    return SizeDetailRecord(
        id=size.id,
        name=size.name,
        width=size.width,
        height=size.height,
        depth=size.depth,
        circumference=size.circumference,
    )


####################
# Variant services #
####################


def variant_create(
    *,
    name: str,
    thumbnail: ImageFile | InMemoryUploadedFile | UploadedFile | None = None,
    is_standard: bool = False,
) -> VariantDetailRecord:
    """
    Creates a Variant with given fields.
    """

    assert name, "Name is required to create a variant."

    new_variant = Variant.objects.create(name=name.title(), is_standard=is_standard)

    # Variants needs an id to save files because the folder structure is
    # <id>-<name>/file, therefore we have to create the variant first,
    # then save the thumbnail file.
    if thumbnail:
        image_validate(
            image=thumbnail,
            allowed_extensions=[".jpg", ".jpeg"],
            width_min_px=370,
            width_max_px=450,
            height_min_px=575,
            height_max_px=690,
        )

        new_variant.thumbnail.save(f"{slugify(new_variant.name)}", thumbnail)

    return VariantDetailRecord(
        id=new_variant.id,
        name=new_variant.name,
        image_url=new_variant.image.url if new_variant.image else None,
        thumbnail_url=new_variant.thumbnail.url if new_variant.thumbnail else None,
        is_standard=new_variant.is_standard,
    )
