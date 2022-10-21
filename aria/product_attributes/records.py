from decimal import Decimal

from pydantic import BaseModel


class ColorDetailRecord(BaseModel):
    id: int
    name: str
    color_hex: str


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


class ShapeDetailRecord(BaseModel):
    id: int
    name: str
    image: str | None
