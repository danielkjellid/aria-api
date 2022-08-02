from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from aria.products.records import ProductRecord


class DiscountProductRecord(BaseModel):
    id: int
    name: str
    description: str | None
    slug: str | None

    products: list[ProductRecord]

    minimum_quantity: int | None
    maximum_quantity: int | None

    discount_gross_price: Decimal | None
    discount_gross_percentage: Decimal | None

    maximum_sold_quantity: int | None
    total_sold_quantity: int | None
    display_maximum_quantity: bool

    active_at: datetime | None
    active_to: datetime | None

    ordering: int | None
