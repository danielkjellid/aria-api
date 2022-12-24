from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING, TypeVar

from pydantic import BaseModel

if TYPE_CHECKING:
    from aria.users.models import User


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
    permissions: list[str]

    @classmethod
    def from_user(
        cls, user: "User", permissions: list[str] | None = None
    ) -> "UserRecord":
        """
        Generate user record from model.
        """

        return cls(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            profile=UserProfileRecord(
                full_name=user.full_name,
                avatar_color=user.avatar_color,
                initial=user.initial,
            ),
            birth_date=user.birth_date,
            phone_number=user.phone_number,
            has_confirmed_email=user.has_confirmed_email,
            street_address=user.street_address,
            zip_code=user.zip_code,
            zip_place=user.zip_place,
            disabled_emails=user.disabled_emails,
            subscribed_to_newsletter=user.subscribed_to_newsletter,
            allow_personalization=user.allow_personalization,
            allow_third_party_personalization=user.allow_third_party_personalization,
            acquisition_source=user.acquisition_source,
            date_joined=user.date_joined,
            is_active=user.is_active,
            is_staff=user.is_staff,
            is_superuser=user.is_superuser,
            permissions=permissions if permissions else [],
        )


class UserNotesRecord(BaseModel):
    id: int
    note: str
    updated_at: datetime
    author: UserProfileRecord


class UserAuditLogsRecord(BaseModel):
    author: str
    change: str
    date_of_change: str
