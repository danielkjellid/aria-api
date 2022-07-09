from pydantic import BaseModel


class NoteEntryRecord(BaseModel):
    id: int
    author_id: int | None
    note: str
