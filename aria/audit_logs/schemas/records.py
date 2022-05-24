from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class LogEntryChangeRecord(BaseModel):
    field: str
    old_value: str | int | Decimal | None
    new_value: str | int | Decimal | None


class LogEntryRecord(BaseModel):
    id: int
    author_id: int
    change: LogEntryChangeRecord
    created_at: datetime
