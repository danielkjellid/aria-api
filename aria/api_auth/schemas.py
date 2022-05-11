from ninja import Schema
from aria.api_auth.records import JWTPair


class TokensObtainInput(Schema):
    email: str
    password: str


class TokensObtainOutput(Schema, JWTPair):
    pass


class TokensRefreshInput(Schema):
    refresh_token: str


class TokensRefreshOutput(Schema, JWTPair):
    pass


class TokenBlacklistInput(Schema):
    refresh_token: str
