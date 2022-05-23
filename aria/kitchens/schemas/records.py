from decimal import Decimal

from pydantic import BaseModel

from aria.core.schemas.records import BaseHeaderImageRecord, BaseListImageRecord


class KitchenVariantRecord(BaseModel):
    id: int
    name: str
    image: str


class KitchenVariantColorRecord(BaseModel):
    id: int
    name: str
    color_hex: str


class KitchenSupplierRecord(BaseModel):
    id: int
    name: str


class KitchenDetailRecord(BaseModel):
    id: int
    name: str
    slug: str
    supplier: KitchenSupplierRecord
    description: str
    extra_description: str
    example_from_price: Decimal
    can_be_painted: bool
    silk_variants: list[KitchenVariantColorRecord]
    decor_variants: list[KitchenVariantRecord]
    plywood_variants: list[KitchenVariantRecord]
    laminate_variants: list[KitchenVariantColorRecord]
    exclusive_variants: list[KitchenVariantColorRecord]
    trend_variants: list[KitchenVariantColorRecord]
    images: BaseHeaderImageRecord
    list_images: BaseListImageRecord
