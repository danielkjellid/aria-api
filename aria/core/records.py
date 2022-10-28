from django.core.files.images import ImageFile

from pydantic import BaseModel


class SiteRecord(BaseModel):
    domain: str
    name: str


class BaseHeaderImageRecord(BaseModel):
    apply_filter: bool
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


class BaseArrayFieldLabelRecord(BaseModel):
    name: str


class BaseImageFullScreenWidthRecord(BaseModel):
    image1440x810: str


# class BaseImageRecord(BaseModel):
#     host: str
#     image_name: str
#     plain_url: str
#     signing_key: str
#     width: int | None
#     height: int | None
#     url: str
#
#     @classmethod
#     def from_image(cls, image: ImageFile) -> "BaseImageRecord":
#         return cls(
#             host=THUMBOR_SERVER_URL,
#             signing_key=generate_signing_key(
#                 image_name=image.name, width=image.width, height=image.height
#             ),
#             plain_url=generate_thumbor_plain_url(
#                 image_name=image.name, width=image.width, height=image.height
#             ),
#             image_name=image.name,
#             width=image.width,
#             height=image.height,
#             url=generate_signed_url(
#                 image_name=image.name, width=image.width, height=image.height
#             ),
#         )
