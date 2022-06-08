from decimal import Decimal

from pydantic import BaseModel

from aria.categories.schemas.records import CategoryDetailRecord
from aria.core.schemas.records import BaseArrayFieldLabelRecord, BaseHeaderImageRecord


class ProductSupplierRecord(BaseModel):
    id: int
    name: str
    origin_country: str
    origin_country_flag: str


class ProductColorRecord(BaseModel):
    id: int
    name: str
    color_hex: str


class ProductVariantRecord(BaseModel):
    id: int
    name: str
    image: str | None
    thumbnail: str | None
    is_standard: bool = False


class ProductSizeRecord(BaseModel):
    id: int
    width: Decimal | None = None
    height: Decimal | None = None
    depth: Decimal | None = None
    circumference: Decimal | None = None
    name: str


class ProductOptionRecord(BaseModel):
    id: int
    gross_price: Decimal
    status: str
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
    status: str
    slug: str
    search_keywords: str | None = None
    short_description: str | None = None
    description: str | None = None
    new_description: str
    unit: str
    vat_rate: float
    available_in_special_sizes: bool = False
    absorption: float | None = None
    is_imported_from_external_source: bool = False
    rooms: list[BaseArrayFieldLabelRecord] | None = []
    materials: list[BaseArrayFieldLabelRecord] | None = []
    thumbnail: str | None


class ProductDetailRecord(ProductRecord):
    from_price: float
    display_price: float
    can_be_picked_up: bool
    can_be_purchased_online: bool
    colors: list[ProductColorRecord] = []
    shapes: list[ProductShapeRecord] = []
    categories: list[CategoryDetailRecord]
    options: list[ProductOptionRecord] = []
    images: list[BaseHeaderImageRecord] = []
    files: list[ProductFileRecord] = []
