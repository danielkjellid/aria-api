from decimal import Decimal

from aria.product_attributes.models import Size
from aria.product_attributes.records import SizeDetailRecord, SizeRecord
from aria.product_attributes.selectors import size_list_from_mapped_values
from aria.product_attributes.utils import (
    size_clean_and_validate_value,
    size_clean_and_validate_values,
)


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
