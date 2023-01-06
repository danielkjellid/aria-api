from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from aria.product_attributes import models


class ColorDetailRecord(BaseModel):
    id: int
    name: str
    color_hex: str


class MaterialDetailRecord(BaseModel):
    id: int
    name: str

    @classmethod
    def from_material(cls, material: models.Material) -> MaterialDetailRecord:
        return cls(id=material.id, name=material.name)


class RoomDetailRecord(BaseModel):
    id: int
    name: str

    @classmethod
    def from_room(cls, room: models.Room) -> RoomDetailRecord:
        return cls(id=room.id, name=room.name)


class ShapeDetailRecord(BaseModel):
    id: int
    name: str
    image_url: str | None


class SizeRecord(BaseModel):
    width: Decimal | None = None
    height: Decimal | None = None
    depth: Decimal | None = None
    circumference: Decimal | None = None


class SizeDetailRecord(BaseModel):
    id: int
    name: str
    width: Decimal | None = None
    height: Decimal | None = None
    depth: Decimal | None = None
    circumference: Decimal | None = None


class VariantDetailRecord(BaseModel):
    id: int
    name: str
    image_url: str | None
    image80x80_url: str | None
    image380x575_url: str | None
    is_standard: bool = False
