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
from aria.products.records import ProductRecord, ProductSupplierRecord
from aria.suppliers.models import Supplier


@transaction.atomic
def product_update(
    *,
    product: Product | None = None,
    name: str,
    supplier: Supplier,
    status: ProductStatus = ProductStatus.AVAILABLE,
    slug: str,
    search_keywords: str | None = None,
    description: str,
    unit: ProductUnit = ProductUnit.PCS,
    category_ids: list[int] | None = None,
    shape_ids: list[int] | None = None,
    color_ids: list[int] | None = None,
    vat_rate: Decimal | float = Decimal("0.25"),
    available_in_special_sizes: bool = False,
    materials: list[str] | None = None,
    rooms: list[str] | None = None,
    absorption: float | None = None,
    display_price: bool = False,
    can_be_purchased_online: bool = False,
    can_be_picked_up: bool = False,
    is_imported_from_external_source: bool = False,
    thumbnail: UploadedFile | InMemoryUploadedFile | ImageFile | None = None,
) -> ProductRecord:

    changes = {
        "name": name,
        "slug": slug,
        "supplier_id": supplier.id,
        "status": status,
        "search_keywords": search_keywords,
        "description": description,
        "unit": unit,
        "vat_rate": vat_rate,
        "available_in_special_sizes": available_in_special_sizes,
        "absorption": absorption,
        "display_price": display_price,
        "can_be_purchased_online": can_be_purchased_online,
        "can_be_picked_up": can_be_picked_up,
        "is_imported_from_external_source": is_imported_from_external_source,
    }

    field_changes = []
    non_side_effect_fields = [k for k in changes.keys()]

    def _update_attribute(
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
        _update_attribute(
            attribute="categories",
            qs=product.categories.all(),
            ids_to_compare=category_ids,
            attribute_qs=Category.objects.select_related("parent"),
            display_property="display_name",
        )

    if shape_ids:
        _update_attribute(
            attribute="shapes",
            qs=product.shapes.all(),
            ids_to_compare=shape_ids,
            attribute_qs=Shape.objects.all(),
            display_property="name",
        )

    if color_ids:
        _update_attribute(
            attribute="colors",
            qs=product.colors.all(),
            ids_to_compare=color_ids,
            attribute_qs=Color.objects.all(),
            display_property="name",
        )

    product, has_updated, updated_fields = model_update(
        instance=product, fields=non_side_effect_fields, data=changes
    )

    field_changes.extend(updated_fields)


@transaction.atomic
def product_create(
    *,
    name: str,
    supplier: Supplier,
    status: ProductStatus = ProductStatus.AVAILABLE,
    slug: str,
    search_keywords: str | None = None,
    description: str,
    unit: ProductUnit = ProductUnit.PCS,
    category_ids: list[int] | None = None,
    shape_ids: list[int] | None = None,
    color_ids: list[int] | None = None,
    vat_rate: Decimal | float = Decimal("0.25"),
    available_in_special_sizes: bool = False,
    materials: list[str] | None = None,
    rooms: list[str] | None = None,
    absorption: float | None = None,
    display_price: bool = False,
    can_be_purchased_online: bool = False,
    can_be_picked_up: bool = False,
    is_imported_from_external_source: bool = False,
    thumbnail: UploadedFile | InMemoryUploadedFile | ImageFile | None = None,
) -> ProductRecord:

    changes = {
        "name": name,
        "slug": slug,
        "supplier_id": supplier.id,
        "status": status,
        "search_keywords": search_keywords,
        "description": description,
        "unit": unit,
        "vat_rate": vat_rate,
        "available_in_special_sizes": available_in_special_sizes,
        "absorption": absorption,
        "display_price": display_price,
        "can_be_purchased_online": can_be_purchased_online,
        "can_be_picked_up": can_be_picked_up,
        "is_imported_from_external_source": is_imported_from_external_source,
    }

    product = Product.objects.create(**changes)

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

    product.save()

    return ProductRecord(
        id=product.id,
        name=product.name,
        supplier=ProductSupplierRecord(
            id=supplier.id,
            name=supplier.name,
            origin_country=supplier.country_name,
            origin_country_flag=supplier.unicode_flag,
        ),
        status=product.status_display,
        slug=product.slug,
        search_keywords=product.search_keywords,
        description=product.description,
        unit=product.unit_display,
        vat_rate=product.vat_rate,
        available_in_special_sizes=product.available_in_special_sizes,
        absorption=product.absorption,
        is_imported_from_external_source=product.is_imported_from_external_source,
        rooms=product.rooms_display,
        materials=product.materials_display,
        thumbnail=product.thumbnail.url if product.thumbnail else None,
    )
