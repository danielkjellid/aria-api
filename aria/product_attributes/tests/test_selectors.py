from decimal import Decimal
from unittest.mock import ANY

import pytest

from aria.product_attributes.records import (
    ColorDetailRecord,
    MaterialDetailRecord,
    RoomDetailRecord,
    ShapeDetailRecord,
    SizeDetailRecord,
    SizeRecord,
    VariantDetailRecord,
)
from aria.product_attributes.selectors import (
    color_list,
    material_list,
    room_list,
    shape_list,
    size_list_from_mapped_values,
    variant_list,
)
from aria.product_attributes.tests.utils import (
    create_color,
    create_material,
    create_room,
    create_shape,
    create_size,
    create_variant,
)

pytestmark = pytest.mark.django_db


class TestProductAttributesSelectors:
    def test_selector_color_list(self, django_assert_max_num_queries):
        """
        Test that the color_list selector returns expected output withing query limits.
        """

        color_1 = create_color(name="Test color 1", color_hex="#FFFFFF")
        color_2 = create_color(name="Test color 2", color_hex="#CCCCCC")
        color_3 = create_color(name="Test color 3", color_hex="#BBBBBB")
        color_4 = create_color(name="Test color 4", color_hex="#333333")

        expected_output = [
            ColorDetailRecord(id=color_4.id, name="Test color 4", color_hex="#333333"),
            ColorDetailRecord(id=color_3.id, name="Test color 3", color_hex="#BBBBBB"),
            ColorDetailRecord(id=color_2.id, name="Test color 2", color_hex="#CCCCCC"),
            ColorDetailRecord(id=color_1.id, name="Test color 1", color_hex="#FFFFFF"),
        ]

        with django_assert_max_num_queries(1):
            colors = color_list()

        assert colors == expected_output

    def test_selector_material_list(self, django_assert_max_num_queries):
        """
        Test that the material_list selector returns expected output withing query
        limits.
        """

        material_1 = create_material(name="Composite")
        material_2 = create_material(name="Wood")
        material_3 = create_material(name="Metal")
        material_4 = create_material(name="Steel")

        expected_output = [
            MaterialDetailRecord(id=material_4.id, name="Steel"),
            MaterialDetailRecord(id=material_3.id, name="Metal"),
            MaterialDetailRecord(id=material_2.id, name="Wood"),
            MaterialDetailRecord(id=material_1.id, name="Composite"),
        ]

        with django_assert_max_num_queries(1):
            materials = material_list()

        assert materials == expected_output

    def test_selector_room_list(self, django_assert_max_num_queries):
        """
        Test that the room_list selector returns expected output withing query limits.
        """

        room_1 = create_room(name="Bathroom")
        room_2 = create_room(name="Hallway")
        room_3 = create_room(name="Kitchen")
        room_4 = create_room(name="Bedroom")

        expected_output = [
            RoomDetailRecord(id=room_4.id, name="Bedroom"),
            RoomDetailRecord(id=room_3.id, name="Kitchen"),
            RoomDetailRecord(id=room_2.id, name="Hallway"),
            RoomDetailRecord(id=room_1.id, name="Bathroom"),
        ]

        with django_assert_max_num_queries(1):
            rooms = room_list()

        assert rooms == expected_output

    def test_selector_shape_list(self, django_assert_max_num_queries):
        """
        Test that the shapes_list selector returns expected output within query limits.
        """

        shape_1 = create_shape(name="Shape 1")
        shape_2 = create_shape(name="Shape 2")
        shape_3 = create_shape(name="Shape 3")
        shape_4 = create_shape(name="Shape 4")

        expected_output = [
            ShapeDetailRecord(
                id=shape_4.id,
                name="Shape 4",
                image_url=shape_4.image.url if shape_4.image else None,
            ),
            ShapeDetailRecord(
                id=shape_3.id,
                name="Shape 3",
                image_url=shape_3.image.url if shape_3.image else None,
            ),
            ShapeDetailRecord(
                id=shape_2.id,
                name="Shape 2",
                image_url=shape_2.image.url if shape_2.image else None,
            ),
            ShapeDetailRecord(
                id=shape_1.id,
                name="Shape 1",
                image_url=shape_1.image.url if shape_1.image else None,
            ),
        ]

        with django_assert_max_num_queries(1):
            shapes = shape_list()

        assert shapes == expected_output

    def test_selector_size_list_from_mapped_values(self, django_assert_max_num_queries):
        """
        Test that the size_list_from_mapped_values correctly mappes unique values to
        record instances.
        """

        size_1 = create_size(
            width=Decimal("20.0"), height=Decimal("40.0"), depth=Decimal("10.0")
        )
        size_2 = create_size(
            width=Decimal("30.0"), height=Decimal("40.0"), depth=Decimal("5.0")
        )
        size_3 = create_size(
            width=Decimal("20.0"), height=Decimal("10.0"), depth=Decimal("5.0")
        )
        size_4 = create_size(width=Decimal("25.0"), height=Decimal("35.0"))
        size_5 = create_size(
            width=Decimal("80.5"), height=Decimal("39.0"), depth=Decimal("12.0")
        )
        size_6 = create_size(circumference=Decimal("30.0"))
        size_7 = create_size(circumference=Decimal("40.0"))
        size_8 = create_size(circumference=Decimal("14.0"))

        size_values_to_map = [
            SizeRecord(width=20.0, height=40.0, depth=10.0),
            SizeRecord(width=30.0, height=40.0, depth=5.0),
            SizeRecord(width=20.0, height=10.0, depth=5.0),
            SizeRecord(width=25.0, height=35.0, depth=12.0),
            SizeRecord(width=80.5, height=35.0, depth=12.0),
            SizeRecord(circumference=30.0),
            SizeRecord(circumference=30.0),
            SizeRecord(circumference=40.0),
            SizeRecord(circumference=14.0),
        ]

        expected_output = [
            SizeDetailRecord.construct(
                id=size_8.id,
                width=None,
                height=None,
                depth=None,
                circumference=Decimal("14"),
                name=ANY,
            ),
            SizeDetailRecord.construct(
                id=size_7.id,
                width=None,
                height=None,
                depth=None,
                circumference=Decimal("40"),
                name=ANY,
            ),
            SizeDetailRecord.construct(
                id=size_6.id,
                width=None,
                height=None,
                depth=None,
                circumference=Decimal("30"),
                name=ANY,
            ),
            SizeDetailRecord.construct(
                id=size_5.id,
                width=Decimal("80.5"),
                height=Decimal("39.0"),
                depth=Decimal("12.0"),
                circumference=None,
                name=ANY,
            ),
            SizeDetailRecord.construct(
                id=size_4.id,
                width=Decimal("25.0"),
                height=Decimal("35.0"),
                depth=None,
                circumference=None,
                name=ANY,
            ),
            SizeDetailRecord.construct(
                id=size_3.id,
                width=Decimal("20.0"),
                height=Decimal("10.0"),
                depth=Decimal("5.0"),
                circumference=None,
                name=ANY,
            ),
            SizeDetailRecord.construct(
                id=size_2.id,
                width=Decimal("30.0"),
                height=Decimal("40.0"),
                depth=Decimal("5.0"),
                circumference=None,
                name=ANY,
            ),
            SizeDetailRecord.construct(
                id=size_1.id,
                width=Decimal("20.0"),
                height=Decimal("40.0"),
                depth=Decimal("10.0"),
                circumference=None,
                name=ANY,
            ),
        ]

        with django_assert_max_num_queries(1):
            mapped_values = size_list_from_mapped_values(values=size_values_to_map)

        # There is 1 duplicate in the list, circumference 30.0, so make sure that this
        # is not returned twice.
        assert len(mapped_values) == len(size_values_to_map) - 1
        assert mapped_values == expected_output

    def test_selector_variant_list(self, django_assert_max_num_queries):
        """
        Test that the variant_list selector returns expected output withing query
        limits.
        """

        variant_1 = create_variant(name="Variant 1", is_standard=False)
        variant_2 = create_variant(name="Variant 2", is_standard=False)
        variant_3 = create_variant(name="Variant 3", is_standard=True)
        variant_4 = create_variant(name="Variant 4", is_standard=False)

        expected_output = [
            VariantDetailRecord(
                id=variant_4.id,
                name="Variant 4",
                is_standard=False,
                image_url=variant_4.image_url,
                image80x80_url=variant_4.image80x80_url,
                image380x575_url=variant_4.image380x575_url,
            ),
            VariantDetailRecord(
                id=variant_3.id,
                name="Variant 3",
                is_standard=True,
                image_url=variant_3.image_url,
                image80x80_url=variant_3.image80x80_url,
                image380x575_url=variant_3.image380x575_url,
            ),
            VariantDetailRecord(
                id=variant_2.id,
                name="Variant 2",
                is_standard=False,
                image_url=variant_2.image_url,
                image80x80_url=variant_2.image80x80_url,
                image380x575_url=variant_2.image380x575_url,
            ),
            VariantDetailRecord(
                id=variant_1.id,
                name="Variant 1",
                is_standard=False,
                image_url=variant_1.image_url,
                image80x80_url=variant_1.image80x80_url,
                image380x575_url=variant_1.image380x575_url,
            ),
        ]

        with django_assert_max_num_queries(1):
            variants = variant_list()

        assert variants == expected_output
