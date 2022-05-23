from pydantic import BaseModel


class SiteRecord(BaseModel):
    domain: str
    name: str


class BaseHeaderImageRecord(BaseModel):
    apply_filter: bool = False
    image_640x275: str | None
    image_1024x1024: str | None
    image_512x512: str | None
    image_1024x575: str | None
    image_1536x860: str | None
    image_2048x1150: str | None


class BaseListImageRecord(BaseModel):
    image500x305: str | None
    image600x440: str | None
    image850x520: str | None
