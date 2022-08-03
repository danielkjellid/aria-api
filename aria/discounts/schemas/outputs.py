from ninja import Schema


class DiscountProductVariantOutput(Schema):
    pass


class DiscountProductSupplierOutput(Schema):
    name: str
    origin_country: str
    origin_country_flag: str


class DiscountProductListOutput(Schema):
    id: int
    name: str
    slug: str
    unit: str
    supplier: DiscountProductSupplierOutput
    thumbnail: str | None
    display_price: bool
    from_price: float
    colors: list
