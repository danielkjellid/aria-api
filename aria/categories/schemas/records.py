from pydantic import BaseModel


class CategoryRecord(BaseModel):
    id: int
    name: str
    slug: str
    ordering: int
    parent: int | None


class CategoryDetailRecord(BaseModel):
    id: int
    name: str
    ordering: int
    slug: str
    description: str
    parent: int | None
    parents: list[CategoryRecord]
    children: list[CategoryRecord]
