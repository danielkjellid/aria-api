from decimal import Decimal

from pydantic import BaseModel


class ColorDetailRecord(BaseModel):
    id: int
    name: str
    color_hex: str


class ShapeDetailRecord(BaseModel):
    id: int
    name: str
    image: str | None


class SizeRecord(BaseModel):
    width: Decimal | None = None
    height: Decimal | None = None
    depth: Decimal | None = None
    circumference: Decimal = None


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
    thumbnail_url: str | None
    is_standard: bool = False
