from decimal import Decimal

from pydantic import BaseModel

from aria.core.schemas.records import BaseHeaderImageRecord


class CategoryRecord(BaseModel):
    id: int
    name: str
    slug: str
    description: str
    ordering: int
    parent: int | None
    images: BaseHeaderImageRecord


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


class CategoryProductRecord(BaseModel):
    id: int
    name: str
    slug: str
    unit: str
    thumbnail: str = None
    display_price: bool | None = False
    from_price: Decimal
    materials: list[str]
    rooms: list[str]
    colors: list[CategoryProductColorRecord]
    shapes: list[CategoryProductShapeRecord]
    variants: list[CategoryProductVariantRecord]
