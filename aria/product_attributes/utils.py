import json
from decimal import Decimal

from django.db import transaction
from django.db.models import Count
from django.utils.translation import gettext as _

from aria.core.exceptions import ApplicationError
from aria.product_attributes.models import Material, Room
from aria.product_attributes.records import SizeRecord
from aria.products.models import Product


def size_clean_and_validate_value(
    *,
    width: Decimal | float | None = None,
    height: Decimal | float | None = None,
    depth: Decimal | float | None = None,
    circumference: Decimal | float | None = None,
) -> SizeRecord:
    """
    Clean size values and validate that param combinations are correct.
    """

    if all(param is None for param in (width, height, depth, circumference)):
        raise ValueError("All size params cannot be None!")

    # Convert zero's to None to avoid having dangling 0's in the DB creating multiple
    # of the "same" size.
    width = width if width != 0 else None
    height = height if height != 0 else None
    depth = depth if depth != 0 else None
    circumference = circumference if circumference else None

    size_to_clean = {
        "width": Decimal(width) if width else None,
        "height": Decimal(height) if height else None,
        "depth": Decimal(depth) if depth else None,
        "circumference": Decimal(circumference) if circumference else None,
    }

    _size_validate(**size_to_clean)

    return SizeRecord(**size_to_clean)


def size_clean_and_validate_values(*, sizes: list[SizeRecord]) -> list[SizeRecord]:
    """
    Clean size values for a list of sizes and validate that param combinations are
    correct.
    """

    cleaned_sizes = []

    for size in sizes:
        cleaned_size = size_clean_and_validate_value(
            width=size.width,
            height=size.height,
            depth=size.depth,
            circumference=size.circumference,
        )

        cleaned_sizes.append(cleaned_size)

    return cleaned_sizes


def _size_validate(
    *,
    width: Decimal | None = None,
    height: Decimal | None = None,
    depth: Decimal | None = None,
    circumference: Decimal | None = None,
) -> None:
    """
    Validate that the correct combination of values is present. For example, we do not
    want to populate certain values based on conditions.
    """

    # Make sure that circumferential sizes only has the circumference param sent in.
    if circumference is not None and any(
        param is not None for param in (width, height, depth)
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
    if circumference is None and any(param is None for param in (width, height)):
        raise ApplicationError(
            message=_(
                "Width and height needs to be specified when not making a "
                "circumferential size."
            ),
            extra={
                "width": _("field required."),
                "height": _("field required."),
            },
        )


@transaction.atomic
def populate_room_material_relations() -> None:
    """
    Populate new Room and Material model relations with data.
    """

    print("Starting population of rooms and materials...")
    material_array_field_mapping = [
        {"name": "Kompositt", "value": "kompositt"},
        {"name": "DADOkvarts", "value": "dado kvarts"},
        {"name": "Rustfritt stål", "value": "rustfritt stål"},
        {"name": "Pusset stål", "value": "pusset stål"},
        {"name": "Metall", "value": "metall"},
        {"name": "Tre", "value": "tre"},
        {"name": "Laminat", "value": "laminat"},
        {"name": "Glass", "value": "glass"},
        {"name": "Marmor", "value": "marmor"},
    ]
    materials_in_use = [item["value"] for item in material_array_field_mapping]
    materials = Material.objects.all()

    print(f"{len(materials_in_use)} materials in use...")

    rooms_array_field_mapping = [
        {"name": "Bad", "value": "badrom"},
        {"name": "Kjøkken", "value": "kjøkken"},
        {"name": "Stue, gang og oppholdsrom", "value": "stue gang oppholdsrom"},
        {"name": "Uterom", "value": "uterom"},
    ]
    rooms_in_use = [item["value"] for item in rooms_array_field_mapping]
    rooms = Room.objects.all()

    print(f"{len(rooms_in_use)} rooms in use...")

    products = Product.objects.all()

    print(f"{len(products)} products...")

    products_to_update = []

    for product in products:
        materials_to_set = []
        rooms_to_set = []

        if not product.materials:
            continue

        for material in product.materials:
            if material not in materials_in_use:
                continue

            mapped_dict = next(
                item
                for item in material_array_field_mapping
                if item["value"] == material
            )
            mapped_material = next(
                item for item in materials if item.name == mapped_dict["name"]
            )

            materials_to_set.append(mapped_material)

        if materials_to_set:
            print(
                f"Product {product.id}: {len(product.materials)} materials | "
                f"{len(materials_to_set)} new materials"
            )
            assert len(materials_to_set) == len(product.materials)
            product.new_materials.set(materials_to_set)
            products_to_update.append(product)

        if not product.rooms:
            continue

        for room in product.rooms:
            if room not in rooms_in_use:
                continue

            mapped_dict = next(
                item for item in rooms_array_field_mapping if item["value"] == room
            )

            mapped_room = next(
                item for item in rooms if item.name == mapped_dict["name"]
            )

            rooms_to_set.append(mapped_room)

        if rooms_to_set:
            print(
                f"Product {product.id}: {len(product.rooms)} rooms | "
                f"{len(rooms_to_set)} new rooms"
            )
            assert len(rooms_to_set) == len(product.rooms)
            product.new_rooms.set(rooms_to_set)
            products_to_update.append(product)

    updated_product_ids = {product.id for product in products_to_update}

    print(f"{len(updated_product_ids)} products updated.")

    updated_products = Product.objects.filter(id__in=updated_product_ids).annotate(
        num_rooms=Count("rooms"),
        num_new_rooms=Count("new_rooms"),
        num_materials=Count("materials"),
        num_new_materials=Count("new_materials"),
    )

    pretty_print = json.dumps(
        list(
            updated_products.values(
                "id", "num_rooms", "num_new_rooms", "num_materials", "num_new_materials"
            )
        ),
        indent=4,
    )

    print(f"Updates in detail: {pretty_print}")

    prompt = input("Roll back? (y/N) ")

    if prompt != "N":
        raise ValueError("Rolled back")
