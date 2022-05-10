from ninja import Schema
from pydantic import validator
from django.core.validators import validate_email
from django.contrib.auth.password_validation import validate_password
from aria.core.exceptions import ApplicationError


class UserCreateOutput(Schema):
    id: int
    email: str
    first_name: str
    last_name: str


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
