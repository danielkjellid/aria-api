from ninja import Schema


class TokensObtainInput(Schema):
    email: str
    password: str


class TokensRefreshInput(Schema):
    refresh_token: str


class TokenBlacklistInput(Schema):
    refresh_token: str
