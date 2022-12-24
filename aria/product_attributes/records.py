from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from aria.product_attributes.models import Color, Shape, Size, Variant


class ColorDetailRecord(BaseModel):
    id: int
    name: str
    color_hex: str

    @classmethod
    def from_color(cls, color: Color) -> ColorDetailRecord:
        """
        Generate color detail record from color model.
        """
        return cls(id=color.id, name=color.name, color_hex=color.color_hex)


class ShapeDetailRecord(BaseModel):
    id: int
    name: str
    image_url: str | None

    @classmethod
    def from_shape(cls, shape: Shape) -> ShapeDetailRecord:
        """
        Generate shape detail record from shape model.
        """
        return cls(
            id=shape.id,
            name=shape.name,
            image_url=shape.image_url,
        )


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

    @classmethod
    def from_size(cls, size: Size) -> SizeDetailRecord:
        """
        Generate size detail record from size model.
        """
        return cls(
            id=size.id,
            name=size.name,
            width=size.width,
            height=size.height,
            depth=size.depth,
            circumference=size.circumference,
        )


class VariantDetailRecord(BaseModel):
    id: int
    name: str
    image_url: str | None
    image80x80_url: str | None
    image380x575_url: str | None
    is_standard: bool = False

    @classmethod
    def from_variant(cls, variant: Variant) -> VariantDetailRecord:
        """
        Generate variant detail record from variant model.
        """
        return cls(
            id=variant.id,
            name=variant.name,
            image_url=variant.image_url,
            image80x80_url=variant.image80x80_url,
            image380x575_url=variant.image380x575_url,
        )
