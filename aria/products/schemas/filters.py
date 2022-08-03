from ninja import Schema


class ProductListFilters(Schema):
    search: str | None = None
