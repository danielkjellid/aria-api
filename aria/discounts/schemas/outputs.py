from ninja import Schema

from aria.products.schemas.outputs import ProductListOutput


class DiscountsActiveListOutput(Schema):
    id: int
    name: str
    slug: str | None

    discount_gross_price: float | None
    discount_gross_percentage: float | None

    products: list[ProductListOutput]
