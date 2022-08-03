from ninja import Schema

from aria.products.schemas.outputs import ProductListOutput


class DiscountsActiveListOutput(Schema):
    id: int
    name: str
    slug: str | None

    products: list[ProductListOutput]

    ordering: int
