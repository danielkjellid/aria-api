from decimal import Decimal

from pydantic import BaseModel


class ColorDetailRecord(BaseModel):
    id: int
    name: str
    color_hex: str


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
