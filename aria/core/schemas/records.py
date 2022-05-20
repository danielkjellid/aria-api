from pydantic import BaseModel


class SiteRecord(BaseModel):
    domain: str
    name: str
