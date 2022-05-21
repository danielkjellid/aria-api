from ninja import Schema
from aria.core.schemas.records import BaseHeaderImageRecord
from aria.products.schemas.records import (
    ProductOptionRecord,
    ProductShapeRecord,
    ProductColorRecord,
    ProductFileRecord,
    ProductSupplierRecord,
)
from decimal import Decimal
from aria.products.enums import ProductStatus


class ProductSupplierOutput(Schema):
    name: str
    origin_country: str


class ProductVariantRecord(Schema):
    id: int
    name: str
    image: str | None


class ProductSizeRecord(Schema):
    id: int
    width: Decimal | None = None
    height: Decimal | None = None
    depth: Decimal | None = None
    circumference: Decimal | None = None


class ProductOptionOutput(Schema):
    id: int
    gross_price: Decimal
    status: ProductStatus
    variant: ProductVariantRecord | None
    size: ProductSizeRecord | None


class ProductColorOutput(Schema):
    name: str
    color_hex: str


class ProductShapeOutput(Schema):
    name: str
    image: str | None


class ProductFileOutput(Schema):
    name: str
    file: str | None


class ProductDetailOutput(Schema):
    id: int
    status: str
    unit: str
    name: str
    description: str | None
    absorption: float | None
    materials: list[str] | None = []
    rooms: list[str] | None = []
    available_in_special_sizes: bool = False
    supplier: ProductSupplierOutput
    images: list[BaseHeaderImageRecord] = []
    options: list[ProductOptionOutput] = []
    colors: list[ProductColorOutput] = []
    shapes: list[ProductShapeOutput] = []
    files: list[ProductFileOutput] = []
