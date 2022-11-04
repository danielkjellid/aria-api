from pydantic import BaseModel

from aria.files.records import BaseCollectionListImageRecord, BaseHeaderImageRecord


class CategoryRecord(BaseModel):
    id: int
    name: str
    display_name: str
    slug: str
    description: str
    ordering: int
    parent: int | None
    images: BaseHeaderImageRecord
    list_images: BaseCollectionListImageRecord


class CategoryDetailRecord(BaseModel):
    id: int
    name: str
    display_name: str
    ordering: int
    slug: str
    description: str
    parent: int | None
    parents: list[CategoryRecord]
    children: list[CategoryRecord]
    images: BaseHeaderImageRecord
    list_images: BaseCollectionListImageRecord
