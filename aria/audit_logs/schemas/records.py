from datetime import datetime
from typing import Any

from pydantic import BaseModel


class LogEntryChangeRecord(BaseModel):
    field: str
    old_value: Any
    new_value: Any


class LogEntryRecord(BaseModel):
    id: int
    author_id: int
    change: LogEntryChangeRecord
    created_at: datetime
