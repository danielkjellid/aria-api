from decimal import Decimal

from django.db import transaction
from django.utils.translation import gettext as _

from aria.core.exceptions import ApplicationError
from aria.products.models import Size


def _size_validation(
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


@transaction.atomic
def size_create(
    *,
    width: Decimal | None = None,
    height: Decimal | None = None,
    depth: Decimal | None = None,
    circumference: Decimal | None = None,
) -> Size:
    _size_validation(
        width=width, height=height, depth=depth, circumference=circumference
    )

    size = Size(
        width=Decimal(width),
        height=Decimal(height),
        depth=Decimal(depth),
        circumference=Decimal(circumference),
    )
    size.full_clean()
    size.save()

    return size


@transaction.atomic
def size_get_or_create(
    *,
    width: Decimal | None,
    height: Decimal | None,
    depth: Decimal | None,
    circumference: Decimal | None,
) -> Size:
    """
    Creates a Size with given fields, if size does not already exist.
    """

    _size_validation(
        width=width, height=height, depth=depth, circumference=circumference
    )

    try:
        size = Size.objects.get(
            width=Decimal(width),
            height=Decimal(height),
            depth=Decimal(depth),
            circumference=Decimal(circumference),
        )
    except Size.DoesNotExist:
        size = size_create(
            width=width, height=height, depth=depth, circumference=circumference
        )

    return size
