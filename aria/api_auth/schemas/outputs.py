from ninja import Schema


class TokensObtainOutput(Schema):
    refresh_token: str
    access_token: str


class TokensRefreshOutput(Schema):
    refresh_token: str
    access_token: str
