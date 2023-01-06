from typing import Any

from django.core.files.images import ImageFile
from django.core.files.uploadedfile import InMemoryUploadedFile, UploadedFile
from django.db import transaction
from django.db.models import QuerySet
from django.utils.translation import gettext as _

from aria.audit_logs.types import ChangeMessage
from aria.categories.models import Category
from aria.core.exceptions import ApplicationError
from aria.core.managers import BaseQuerySet
from aria.core.services import model_update
from aria.files.validators import image_validate
from aria.product_attributes.models import Color, Material, Room, Shape
from aria.products.models import Product
from aria.products.records import ProductRecord
from aria.products.selectors.records import product_record
from aria.suppliers.models import Supplier


@transaction.atomic
def product_create(
    *,
    name: str,
    supplier: Supplier,
    category_ids: list[int] | None = None,
    shape_ids: list[int] | None = None,
    color_ids: list[int] | None = None,
    material_ids: list[int] | None = None,
    room_ids: list[int] | None = None,
    thumbnail: UploadedFile | InMemoryUploadedFile | ImageFile | None = None,
    **kwargs: dict[str, Any],
) -> ProductRecord:
    """
    Create a new product instance.
    """

    kwargs.pop("name", None)
    kwargs.pop("supplier_id", None)
    product = Product(name=name, supplier_id=supplier.id, **kwargs)

    if thumbnail is not None:
        image_validate(
            image=thumbnail,
            allowed_extensions=[".jpg", ".jpeg"],
            width_min_px=370,
            width_max_px=450,
            height_min_px=575,
            height_max_px=690,
        )
        product.thumbnail = thumbnail

    product.full_clean()
    product.save()

    if category_ids is not None:
        categories = Category.objects.filter(id__in=category_ids)

        for category in categories:
            if category.is_primary:
                raise ApplicationError(
                    message=_(
                        "You can not add a primary category to products. Tried to add %s."  # pylint: disable=C0209, line-too-long
                        % category.name
                    )
                )

        product.categories.set(categories)

    if material_ids is not None:
        materials = Material.objects.filter(id__in=material_ids)
        product.materials.set(materials)

    if room_ids is not None:
        rooms = Room.objects.filter(id__in=room_ids)
        product.rooms.set(rooms)

    if shape_ids is not None:
        shapes = Shape.objects.filter(id__in=shape_ids)
        product.shapes.set(shapes)

    if color_ids is not None:
        colors = Color.objects.filter(id__in=color_ids)
        product.colors.set(colors)

    # TODO: Add audit logging, and make sure log is correctly in test

    return product_record(product=product)


@transaction.atomic
def product_update(
    *,
    product: Product,
    category_ids: list[int] | None = None,
    shape_ids: list[int] | None = None,
    color_ids: list[int] | None = None,
    material_ids: list[int] | None = None,
    room_ids: list[int] | None = None,
    thumbnail: UploadedFile | InMemoryUploadedFile | ImageFile | None = None,
    **kwargs: dict[str, Any],
) -> ProductRecord:
    """
    Updates an existing product instance.
    """

    field_changes = []
    non_side_effect_fields = [
        "name",
        "slug",
        "supplier",
        "supplier_id",
        "status",
        "search_keywords",
        "description",
        "unit",
        "vat_rate",
        "available_in_special_sizes",
        "absorption",
        "display_price",
        "can_be_purchased_online",
        "can_be_picked_up",
        "is_imported_from_external_source",
        "thumbnail",
    ]

    def _create_log_message(
        *, field: str, old_value: Any, new_value: Any
    ) -> ChangeMessage:
        """
        Quickly create a log message in the expected format.
        """

        log_message: ChangeMessage = {
            "field": field,
            "old_value": old_value,
            "new_value": new_value,
        }

        return log_message

    def _update_side_effect_attribute(
        *,
        attribute: str,
        qs: BaseQuerySet[Any] | QuerySet[Any],
        ids_to_compare: list[int],
        attribute_qs: BaseQuerySet[Any] | QuerySet[Any],
        display_property: str,
    ) -> None:
        """
        Private utility function for updating attributes on received changes.

        * attribute:
            Generic name of the attribute being updated. Typically related name.

        * qs:
            Queryset for fetching the product's set attribute. Usually just
            product.attribute.all().

        * ids_to_compare:
            List of ids received in parent method kwargs. We check if there are actual
            diffs between the passed list and current state. If not, we do nothing.

        * attribute_qs:
            Queryset for fetching the instances received in the diff in ids_to_compare.
            Usually attribute_class.objects.all() - can also contain related prefetches.

        * display_property:
            Property to use when generating change message. Should contain
            human-readable properties.
        """

        product_attribute_qs = qs
        product_attribute_ids = [q.id for q in qs]
        product_attribute = getattr(product, attribute)

        if not ids_to_compare:
            product_attribute.set([])
            return

        if product_attribute_ids != ids_to_compare:
            update_instances = attribute_qs.filter(id__in=ids_to_compare)
            product_attribute.set(update_instances)

            field_changes.append(
                _create_log_message(
                    field=attribute,
                    old_value=[
                        getattr(attr, display_property) for attr in product_attribute_qs
                    ],
                    new_value=[
                        getattr(attr, display_property) for attr in update_instances
                    ],
                )
            )

    if category_ids is not None:
        _update_side_effect_attribute(
            attribute="categories",
            qs=product.categories.all(),
            ids_to_compare=category_ids,
            attribute_qs=Category.objects.select_related("parent"),
            display_property="display_name",
        )

    if shape_ids is not None:
        _update_side_effect_attribute(
            attribute="shapes",
            qs=product.shapes.all(),
            ids_to_compare=shape_ids,
            attribute_qs=Shape.objects.all(),
            display_property="name",
        )

    if color_ids is not None:
        _update_side_effect_attribute(
            attribute="colors",
            qs=product.colors.all(),
            ids_to_compare=color_ids,
            attribute_qs=Color.objects.all(),
            display_property="name",
        )

    if room_ids is not None:
        _update_side_effect_attribute(
            attribute="rooms",
            qs=product.rooms.all(),
            ids_to_compare=room_ids,
            attribute_qs=Room.objects.all(),
            display_property="name",
        )

    if material_ids is not None:
        _update_side_effect_attribute(
            attribute="materials",
            qs=product.materials.all(),
            ids_to_compare=material_ids,
            attribute_qs=Material.objects.all(),
            display_property="name",
        )

    if (
        thumbnail
        and thumbnail.name is not None
        and thumbnail.name != product.thumbnail.name
    ):

        image_validate(
            image=thumbnail,
            allowed_extensions=[".jpg", ".jpeg"],
            width_min_px=370,
            width_max_px=450,
            height_min_px=575,
            height_max_px=690,
        )

        old_thumbnail_url = product.thumbnail.url if product.thumbnail else None
        new_thumbnail_url = product.thumbnail.url if product.thumbnail else None

        if product.thumbnail is not None:
            # This change needs to be saved here for the cleanup signal to be fired.
            product.thumbnail.delete(save=True)

            product.thumbnail = thumbnail

            field_changes.append(
                _create_log_message(
                    field="thumbnail",
                    old_value=old_thumbnail_url,
                    new_value=new_thumbnail_url,
                )
            )

    product, has_updated, updated_fields = model_update(
        instance=product, fields=non_side_effect_fields, data=kwargs
    )

    if has_updated:
        field_changes.extend(updated_fields)
        # TODO: Add audit logging, and make sure log is correctly in test

    return product_record(product=product)
