from pydantic import BaseModel
from decimal import Decimal
from aria.core.schemas.records import BaseHeaderImageRecord
from aria.categories.schemas.records import CategoryDetailRecord
from aria.products.enums import ProductStatus
from aria.products.enums import ProductUnit


class ProductSupplierRecord(BaseModel):
    name: str
    origin_country: str


class ProductColorRecord(BaseModel):
    id: int
    name: str
    color_hex: str


class ProductVariantRecord(BaseModel):
    id: int
    name: str
    image: str | None
    is_standard: bool = False


class ProductSizeRecord(BaseModel):
    id: int
    width: Decimal | None = None
    height: Decimal | None = None
    depth: Decimal | None = None
    circumference: Decimal | None = None


class ProductOptionRecord(BaseModel):
    id: int
    gross_price: Decimal
    status: ProductStatus
    variant: ProductVariantRecord | None
    size: ProductSizeRecord | None


class ProductFileRecord(BaseModel):
    id: int
    name: str
    file: str | None


class ProductShapeRecord(BaseModel):
    id: int
    name: str
    image: str | None


class ProductRecord(BaseModel):
    id: int
    name: str
    supplier: ProductSupplierRecord
    categories: list[CategoryDetailRecord]
    status: ProductStatus
    slug: str
    search_keywords: str | None = None
    short_description: str | None = None
    description: str | None = None
    new_description: str
    unit: ProductUnit
    vat_rate: float
    available_in_special_sizes: bool = False
    colors: list[ProductColorRecord] = []
    shapes: list[ProductShapeRecord] = []
    materials: list[str] | None = []
    rooms: list[str] | None = []
    absorption: float | None = None
    is_imported_from_external_source: bool = False
    files: list[ProductFileRecord] = []
    thumbnail: str | None
    images: list[BaseHeaderImageRecord] = []
    options: list[ProductOptionRecord] = []
