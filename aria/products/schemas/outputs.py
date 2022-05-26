from ninja import Schema

from aria.core.schemas.records import BaseHeaderImageRecord


class ProductSupplierOutput(Schema):
    name: str
    origin_country: str


class ProductVariantOutput(Schema):
    id: int
    name: str
    image: str | None


class ProductSizeOutput(Schema):
    id: int
    name: str


class ProductOptionOutput(Schema):
    id: int
    gross_price: float
    status: str
    variant: ProductVariantOutput | None
    size: ProductSizeOutput | None


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
