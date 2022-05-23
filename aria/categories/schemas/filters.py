from ninja import Schema


class CategoryProductListFilters(Schema):
    search: str = None
