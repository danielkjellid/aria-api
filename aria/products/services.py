from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.files import File
from django.db import transaction
from django.utils.text import slugify
from django.utils.translation import gettext as _

from aria.core.exceptions import ApplicationError
from aria.products.models import ProductOption, Variant, Size


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


@transaction.atomic
def size_create(
    *,
    width: Decimal | None,
    height: Decimal | None,
    depth: Decimal | None,
    circumference: Decimal | None,
) -> Size:
    """
    Creates a Size with given fields, if size does not already exist.
    """

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

    try:
        size = Size(
            width=Decimal(width) if width is not None else None,
            height=Decimal(height) if height is not None else None,
            depth=Decimal(depth) if depth is not None else None,
            circumference=Decimal(circumference) if circumference is not None else None,
        )
        size.full_clean()
        size.save()

        return size
    except ValidationError as exc:
        # If the full_clean() method throws an exception regarding model uniqueness,
        # catch this message as we want to manually handle this exception to the user.
        if (
            isinstance(exc.messages, list)
            and len(exc.messages) == 1
            and exc.messages[0]
            == "Size with this Width, Height, Depth and Circumference already exists."
        ):
            raise ApplicationError(message=_("Size already exist.")) from exc

        raise exc


def product_option_delete_related_variants(*, instance: ProductOption) -> None:
    """
    Cleanup dangling variants that does not belong to other
    products.
    """

    related_variant: Variant | None = instance.variant

    # Check if there are other products that's linked to the same
    # variant while filtering out standards.
    if (
        related_variant is not None
        and related_variant.is_standard is False
        and len(related_variant.product_options.all()) == 1
    ):
        related_variant.delete()
