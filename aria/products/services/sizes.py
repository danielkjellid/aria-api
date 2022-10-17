from decimal import Decimal

from django.utils.translation import gettext as _

from aria.core.exceptions import ApplicationError
from aria.products.models import Size
from aria.products.records import ProductSizeRecord
from aria.products.selectors.sizes import size_list_from_mapped_values
from aria.products.types import SizeDict


def size_create(
    *,
    width: Decimal | None = None,
    height: Decimal | None = None,
    depth: Decimal | None = None,
    circumference: Decimal | None = None,
) -> ProductSizeRecord:
    cleaned_size = size_clean_and_validate_value(
        width=width, height=height, depth=depth, circumference=circumference
    )

    size = Size(
        width=cleaned_size["width"],
        height=cleaned_size["height"],
        depth=cleaned_size["depth"],
        circumference=cleaned_size["circumference"],
    )
    size.full_clean()
    size.save()

    return ProductSizeRecord(
        id=size.id,
        name=size.name,
        width=size.width,
        height=size.height,
        depth=size.depth,
        circumference=size.circumference,
    )


def size_bulk_create(*, sizes: list[SizeDict]) -> list[ProductSizeRecord]:

    sizes_to_create = [
        Size(
            width=size["width"],
            height=size["height"],
            depth=size["depth"],
            circumference=size["circumference"],
        )
        for size in size_clean_and_validate_values(sizes=sizes)
    ]

    Size.objects.bulk_create(sizes_to_create, ignore_conflicts=True)

    # Since we ignore conflicts, not all values passed in are necessarily created.
    # Therefore, we re-fetch all relevant objects and return them instead of the
    # Django's default "all objects that has been created".
    fetched_sizes = size_list_from_mapped_values(values=sizes)

    return [
        ProductSizeRecord(
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
    width: Decimal | None,
    height: Decimal | None,
    depth: Decimal | None,
    circumference: Decimal | None,
) -> ProductSizeRecord | None:
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
            width=cleaned_size["width"],
            height=cleaned_size["height"],
            depth=cleaned_size["depth"],
            circumference=cleaned_size["circumference"],
        )
    except Size.DoesNotExist:
        size = size_create(
            width=width, height=height, depth=depth, circumference=circumference
        )

    return ProductSizeRecord(
        id=size.id,
        name=size.name,
        width=size.width,
        height=size.height,
        depth=size.depth,
        circumference=size.circumference,
    )


def _size_validate(
    *,
    width: Decimal | None = None,
    height: Decimal | None = None,
    depth: Decimal | None = None,
    circumference: Decimal | None = None,
) -> None:

    # Make sure that circumferential sizes only has the circumference param sent in.
    if circumference is not None and any(
        param is not None for param in {width, height, depth}
    ):

        extra_dict = {}

        if width is not None:
            extra_dict["width"] = _(
                "Field cannot be specified when making a circumferential size"
            )
        if height is not None:
            extra_dict["height"] = _(
                "Field cannot be specified when making a circumferential size"
            )
        if depth is not None:
            extra_dict["depth"] = _(
                "Field cannot be specified when making a circumferential size"
            )

        raise ApplicationError(
            message=_(
                "Width, height or depth cannot be specified when making a "
                "circumferential size."
            ),
            extra=extra_dict,
        )

    # Make sure that normal sizes at least have width and height specified.
    if circumference is None and all(param is None for param in {width, height}):
        raise ApplicationError(
            message=_(
                "Width and height needs to be specified when not making a "
                "circumferential size."
            ),
            extra={
                "width": _("This field needs to be specified."),
                "height": _("This field needs to be specified."),
            },
        )


def size_clean_and_validate_value(
    *,
    width: Decimal | None,
    height: Decimal | None,
    depth: Decimal | None,
    circumference: Decimal | None,
) -> SizeDict | None:
    width = width if width != 0 else None
    height = height if height != 0 else None
    depth = depth if depth != 0 else None
    circumference = circumference if circumference else None

    if all(param is None for param in {width, height, depth, circumference}):
        return None

    size_to_clean = {
        "width": Decimal(width) if width else None,
        "height": Decimal(height) if height else None,
        "depth": Decimal(depth) if depth else None,
        "circumference": Decimal(circumference) if circumference else None,
    }

    _size_validate(**size_to_clean)

    return size_to_clean


def size_clean_and_validate_values(*, sizes: list[SizeDict]) -> list[SizeDict]:

    cleaned_sizes = []

    for size in sizes:
        cleaned_size = size_clean_and_validate_value(
            width=size.get("width", None),
            height=size.get("height", None),
            depth=size.get("depth", None),
            circumference=size.get("circumference", None),
        )

        cleaned_sizes.append(cleaned_size)

    return cleaned_sizes
