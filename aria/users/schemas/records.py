from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel

from aria.core.schemas.records import SiteRecord


class UserProfileRecord(BaseModel):
    full_name: str
    initial: str
    avatar_color: str


class UserRecord(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    profile: UserProfileRecord
    birth_date: date | None = None
    phone_number: str
    has_confirmed_email: bool = False
    street_address: str
    zip_code: str
    zip_place: str
    disabled_emails: bool = False
    subscribed_to_newsletter: bool = True
    allow_personalization: bool = True
    allow_third_party_personalization: bool = True
    acquisition_source: str | None
    date_joined: datetime
    is_active: bool = True
    is_staff: bool = False
    is_superuser: bool = False
    site: Optional[SiteRecord] = None


class UserNotesRecord(BaseModel):
    id: int
    note: str
    updated_at: datetime
    author: UserProfileRecord


class UserAuditLogsRecord(BaseModel):
    author: str
    change: str
    date_of_change: str
