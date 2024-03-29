from typing import List

from ninja import Schema

from aria.files.records import BaseCollectionListImageRecord, BaseHeaderImageRecord


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
    list_images: BaseCollectionListImageRecord


class CategoryDetailOutput(Schema):
    id: int
    name: str
    slug: str
    images: BaseHeaderImageRecord
