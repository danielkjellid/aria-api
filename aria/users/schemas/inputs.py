from typing import Optional

from ninja import Schema


class UserCreateInput(Schema):
    email: str
    first_name: str
    last_name: str
    phone_number: str
    street_address: str
    zip_code: str
    zip_place: str
    subscribed_to_newsletter: bool
    allow_personalization: bool
    allow_third_party_personalization: bool
    password: str


class UserAccountVerificationInput(Schema):
    email: str


class UserAccountVerificationConfirmInput(Schema):
    uid: str
    token: str


class UserPasswordResetInput(Schema):
    email: str


class UserPasswordResetConfirmInput(Schema):
    new_password: str
    uid: str
    token: str


class UserUpdateInput(Schema):
    email: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    phone_number: Optional[str]
    has_confirmed_email: Optional[bool]
    street_address: Optional[str]
    zip_code: Optional[str]
    zip_place: Optional[str]
    disabled_emails: Optional[bool]
    subscribed_to_newsletter: Optional[bool]
    allow_personalization: Optional[bool]
    allow_third_party_personalization: Optional[bool]
