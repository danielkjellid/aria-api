from typing import Optional

from ninja import Schema


class CategoryProductListFilters(Schema):
    search: Optional[str] = None
