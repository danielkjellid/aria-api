from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from aria.suppliers.models import Supplier


class SupplierRecord(BaseModel):
    id: int
    name: str
    origin_country_name: str
    origin_country_flag: str
    is_active: bool

    @classmethod
    def from_supplier(cls, supplier: Supplier):
        """
        Generate supplier record from model.
        """
        return cls(
            id=supplier.id,
            name=supplier.name,
            origin_country_name=supplier.country_name,
            origin_country_flag=supplier.unicode_flag,
            is_active=supplier.is_active,
        )
