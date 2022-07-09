from pydantic import BaseModel


class TokenPayload(BaseModel):
    token_type: str
    exp: int
    iat: int
    jti: str
    iss: str
    user_id: int


class JWTPair(BaseModel):
    refresh_token: str
    access_token: str
