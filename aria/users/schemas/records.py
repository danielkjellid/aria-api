from pydantic import BaseModel
from datetime import datetime


class UserProfileRecord(BaseModel):
    full_name: str
    initial: str
    avatar_color: str


class UserNotesRecord(BaseModel):
    id: int
    note: str
    updated_at: datetime
    author: UserProfileRecord


class UserAuditLogsRecord(BaseModel):
    author: str
    change: str
    date_of_change: str
