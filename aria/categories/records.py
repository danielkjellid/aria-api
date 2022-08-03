from pydantic import BaseModel

from aria.core.records import BaseHeaderImageRecord, BaseListImageRecord


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
