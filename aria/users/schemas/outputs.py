from datetime import date, datetime

from ninja import Schema

from aria.users.models import User
from aria.users.records import UserAuditLogsRecord, UserNotesRecord, UserProfileRecord


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
    birth_date: date | None = None
    has_confirmed_email: bool

    # Account data
    last_login: datetime | None = None
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
    acquisition_source: str | None = None
    disabled_emails: bool
    subscribed_to_newsletter: bool
    allow_personalization: bool
    allow_third_party_personalization: bool

    # Notes and logs
    notes: list[UserNotesRecord] = []
    logs: list[UserAuditLogsRecord] = []

    @staticmethod
    def resolve_phone_number(user: User) -> str:
        """
        Return formatted phone number.
        """
        return user.formatted_phone_number

    @staticmethod
    def resolve_notes(user: User) -> list[UserNotesRecord]:
        """
        Retrieve a list of notes belonging to the user
        """
        notes: list[UserNotesRecord] = user.get_notes()
        return notes

    @staticmethod
    def resolve_logs(user: User) -> list[UserAuditLogsRecord]:
        """
        Retrieve a list of audit logs belonging to the user
        """
        audit_logs: list[UserAuditLogsRecord] = user.get_audit_logs()
        return audit_logs
