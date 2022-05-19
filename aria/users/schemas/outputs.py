from ninja import Schema
from datetime import datetime, date
from aria.users.schemas.records import (
    UserProfileRecord,
    UserNotesRecord,
    UserAuditLogsRecord,
)


class UserListOutput(Schema):
    id: int
    email: str
    is_active: bool
    date_joined: datetime
    profile: UserProfileRecord


class UserDetailOutput(Schema):
    first_name: str
    last_name: str
    email: str
    phone_number: str
    birth_date: date
    has_confirmed_email: bool

    # Account data
    last_login: datetime
    id: int
    profile: UserProfileRecord
    date_joined: datetime
    is_active: bool

    # Address data
    full_address: str
    street_address: str
    zip_code: str
    zip_place: str

    # Marketing data
    acquisition_source: str = None
    disabled_emails: bool
    subscribed_to_newsletter: bool
    allow_personalization: bool
    allow_third_party_personalization: bool

    # Notes and logs
    notes: list[UserNotesRecord] = []
    logs: list[UserAuditLogsRecord] = []

    @staticmethod
    def resolve_notes(user) -> list[UserNotesRecord]:
        return user.get_notes()

    @staticmethod
    def resolve_logs(user) -> list[UserAuditLogsRecord]:
        return user.get_audit_logs()
