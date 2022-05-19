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
    email: str
    first_name: str
    last_name: str
    phone_number: str
    has_confirmed_email: bool
    street_address: str
    zip_code: str
    zip_place: str
    disabled_emails: bool
    subscribed_to_newsletter: bool
    allow_personalization: bool
    allow_third_party_personalization: bool
