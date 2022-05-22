from decimal import Decimal
from typing import List

from ninja import Schema

from aria.core.schemas.records import BaseHeaderImageRecord
from aria.products.enums import ProductUnit


class CategoryListOutput(Schema):
    id: int
    name: str
    slug: str
    ordering: int
    children: List[
        "CategoryListOutput"
    ] | None  # Pydantic bug, need to use List instead of list


class CategoryParenListOutput(Schema):
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
    images: BaseHeaderImageRecord


class CategoryProductListColorOutput(Schema):
    id: int
    name: str
    color_hex: str


class CategoryProductListShapeOutput(Schema):
    name: str
    image: str


class CategoryProductListVariantOutput(Schema):
    id: int
    name: str
    thumbnail: str
    image: str


class CategoryProductListOutput(Schema):
    id: int
    name: str
    slug: str
    unit: ProductUnit
    thumbnail: str
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
