from ninja import Schema

from aria.core.records import BaseHeaderImageRecord, BaseListImageRecord


class KitchenListOutput(Schema):
    id: int
    name: str
    slug: str
    thumbnail_description: str
    list_images: BaseListImageRecord


class KitchenVariantOutput(Schema):
    name: str
    image: str


class KitchenVariantColorOutput(Schema):
    name: str
    color_hex: str


class KitchenDetailOutput(Schema):
    id: int
    name: str
    slug: str
    description: str
    extra_description: str
    example_from_price: str | None
    can_be_painted: bool
    silk_variants: list[KitchenVariantColorOutput]
    decor_variants: list[KitchenVariantOutput]
    plywood_variants: list[KitchenVariantOutput]
    laminate_variants: list[KitchenVariantColorOutput]
    exclusive_variants: list[KitchenVariantColorOutput]
    trend_variants: list[KitchenVariantColorOutput]
    images: BaseHeaderImageRecord
