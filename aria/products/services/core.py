from decimal import Decimal
from typing import Any

from django.core.files.images import ImageFile
from django.core.files.uploadedfile import InMemoryUploadedFile, UploadedFile
from django.db import transaction
from django.utils.translation import gettext as _

from aria.categories.models import Category
from aria.core.exceptions import ApplicationError
from aria.core.models import BaseQuerySet
from aria.core.services import model_update
from aria.core.validators import image_validate
from aria.products.enums import (
    ProductMaterials,
    ProductRooms,
    ProductStatus,
    ProductUnit,
)
from aria.products.models import Color, Product, Shape
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
    materials: list[str] | None = None,
    rooms: list[str] | None = None,
    thumbnail: UploadedFile | InMemoryUploadedFile | ImageFile | None = None,
    **kwargs: dict[str, Any],
) -> ProductRecord:

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

    if materials:
        materials_to_add = [
            material for material in materials if material in ProductMaterials
        ]
        product.materials = materials_to_add

    if rooms:
        rooms_to_add = [room for room in rooms if room in ProductRooms]
        product.rooms = rooms_to_add

    product.full_clean()
    product.save()

    if category_ids:
        categories = Category.objects.filter(id__in=category_ids)

        for category in categories:
            if category.is_primary:
                raise ApplicationError(
                    message=_("You may only add secondary categories to products.")
                )

        product.categories.set(categories)

    if shape_ids:
        shapes = Shape.objects.filter(id__in=shape_ids)
        product.shapes.set(shapes)

    if color_ids:
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
    materials: list[str] | None = None,
    rooms: list[str] | None = None,
    thumbnail: UploadedFile | InMemoryUploadedFile | ImageFile | None = None,
    **kwargs: dict[str, Any],
) -> ProductRecord:

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

    def _update_side_effect_attribute(
        *,
        attribute: str,
        qs: BaseQuerySet[Product],
        ids_to_compare: list[int],
        attribute_qs: BaseQuerySet[Any],
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

        if product_attribute_ids != ids_to_compare:
            update_instances = attribute_qs.filter(id__in=ids_to_compare)

            product_attribute = getattr(product, attribute)
            product_attribute.set(update_instances)

            field_changes.append(
                {
                    "field": attribute,
                    "old_value": [
                        getattr(attr, display_property) for attr in product_attribute_qs
                    ],
                    "new_value": [
                        getattr(attr, display_property) for attr in update_instances
                    ],
                }
            )

    if category_ids:
        _update_side_effect_attribute(
            attribute="categories",
            qs=product.categories.all(),
            ids_to_compare=category_ids,
            attribute_qs=Category.objects.select_related("parent"),
            display_property="display_name",
        )

    if shape_ids:
        _update_side_effect_attribute(
            attribute="shapes",
            qs=product.shapes.all(),
            ids_to_compare=shape_ids,
            attribute_qs=Shape.objects.all(),
            display_property="name",
        )

    if color_ids:
        _update_side_effect_attribute(
            attribute="colors",
            qs=product.colors.all(),
            ids_to_compare=color_ids,
            attribute_qs=Color.objects.all(),
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
            {
                "field": "thumbnail",
                "old_value": old_thumbnail_url,
                "new_value": new_thumbnail_url,
            }
        )

    if materials:
        product_materials = product.materials
        materials_to_add = [
            material for material in materials if material in ProductMaterials
        ]

        if product_materials != materials_to_add:
            product.materials = materials_to_add

            field_changes.append(
                {
                    "field": "materials",
                    "old_value": product_materials,
                    "new_value": materials_to_add,
                }
            )

    if rooms:
        product_rooms = product.rooms
        rooms_to_add = [room for room in rooms if room in ProductRooms]

        if product_rooms != rooms_to_add:
            product.rooms = rooms_to_add

            field_changes.append(
                {
                    "field": "rooms",
                    "old_value": product_rooms,
                    "new_value": rooms_to_add,
                }
            )

    product, has_updated, updated_fields = model_update(
        instance=product, fields=non_side_effect_fields, data=kwargs
    )

    if has_updated:
        field_changes.extend(updated_fields)
        # TODO: Add audit logging, and make sure log is correctly in test

    return product_record(product=product)
