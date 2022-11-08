from decimal import Decimal

from pydantic import BaseModel

from aria.files.records import BaseCollectionListImageRecord, BaseHeaderImageRecord


class KitchenVariantRecord(BaseModel):
    id: int
    name: str
    image_url: str | None
    image80x80_url: str | None


class KitchenVariantColorRecord(BaseModel):
    id: int
    name: str
    color_hex: str


class KitchenSupplierRecord(BaseModel):
    id: int
    name: str


class KitchenRecord(BaseModel):
    id: int
    name: str
    slug: str
    supplier: KitchenSupplierRecord
    thumbnail_description: str
    list_images: BaseCollectionListImageRecord


class KitchenDetailRecord(KitchenRecord):
    description: str
    extra_description: str | None
    example_from_price: Decimal | None
    can_be_painted: bool
    silk_variants: list[KitchenVariantColorRecord]
    decor_variants: list[KitchenVariantRecord]
    plywood_variants: list[KitchenVariantRecord]
    laminate_variants: list[KitchenVariantColorRecord]
    exclusive_variants: list[KitchenVariantColorRecord]
    trend_variants: list[KitchenVariantColorRecord]
    images: BaseHeaderImageRecord
