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
    email: str | None
    first_name: str | None
    last_name: str | None
    phone_number: str | None
    has_confirmed_email: bool | None
    street_address: str | None
    zip_code: str | None
    zip_place: str | None
    disabled_emails: bool | None
    subscribed_to_newsletter: bool | None
    allow_personalization: bool | None
    allow_third_party_personalization: bool | None
