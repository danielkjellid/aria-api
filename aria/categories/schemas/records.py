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
