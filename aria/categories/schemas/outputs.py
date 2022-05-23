from decimal import Decimal
from typing import List

from ninja import Schema

from aria.core.schemas.records import BaseHeaderImageRecord, BaseListImageRecord


class CategoryListOutput(Schema):
    id: int
    name: str
    slug: str
    ordering: int
    children: List[
        "CategoryListOutput"
    ] | None  # Pydantic bug, need to use List instead of list


class CategoryParentListOutput(Schema):
    id: int
    name: str
    slug: str
    ordering: int
    images: BaseHeaderImageRecord


class CategoryChildrenListOutput(Schema):
    id: int
    name: str
    slug: str
    ordering: int
    description: str
    list_images: BaseListImageRecord


class CategoryProductListColorOutput(Schema):
    id: int
    name: str
    color_hex: str


class CategoryProductListShapeOutput(Schema):
    id: int
    name: str
    image: str


class CategoryProductListVariantOutput(Schema):
    id: int
    name: str
    thumbnail: str | None
    image: str | None


class CategoryProductListOutput(Schema):
    id: int
    name: str
    slug: str
    unit: str
    thumbnail: str | None
    display_price: bool
    from_price: Decimal
    colors: list[CategoryProductListColorOutput]
    shapes: list[CategoryProductListShapeOutput]
    materials: list[str]
    variants: list[CategoryProductListVariantOutput]


class CategoryDetailOutput(Schema):
    id: int
    name: str
    slug: str
    images: BaseHeaderImageRecord
