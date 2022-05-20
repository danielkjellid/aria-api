from ninja import Schema, Field


class SupplierListOutput(Schema):
    id: int
    name: str
    website_link: str
    logo: str = Field(..., alias="image.url")
