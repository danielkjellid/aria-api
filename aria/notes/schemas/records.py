from pydantic import BaseModel


class NoteEntryRecord(BaseModel):
    author: int
    note: str
