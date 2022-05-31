from decimal import Decimal

from pydantic import BaseModel

from aria.core.schemas.records import BaseHeaderImageRecord, BaseListImageRecord


class CategoryRecord(BaseModel):
    id: int
    name: str
    slug: str
    description: str
    ordering: int
    parent: int | None
    images: BaseHeaderImageRecord
    list_images: BaseListImageRecord


class CategoryDetailRecord(BaseModel):
    id: int
    name: str
    ordering: int
    slug: str
    description: str
    parent: int | None
    parents: list[CategoryRecord]
    children: list[CategoryRecord]
    images: BaseHeaderImageRecord
    list_images: BaseListImageRecord


class CategoryProductColorRecord(BaseModel):
    id: int
    name: str
    color_hex: str


class CategoryProductShapeRecord(BaseModel):
    id: int
    name: str
    image: str | None


class CategoryProductVariantRecord(BaseModel):
    id: int
    name: str
    thumbnail: str | None
    image: str | None


class CategoryProductSupplierRecord(BaseModel):
    id: int
    name: str
    origin_country: str
    origin_country_flag: str


class CategoryProductRecord(BaseModel):
    id: int
    name: str
    slug: str
    unit: str
    supplier: CategoryProductSupplierRecord
    thumbnail: str = None
    display_price: bool | None = False
    from_price: Decimal
    materials: list[str]
    rooms: list[str]
    colors: list[CategoryProductColorRecord]
    shapes: list[CategoryProductShapeRecord]
    variants: list[CategoryProductVariantRecord]
