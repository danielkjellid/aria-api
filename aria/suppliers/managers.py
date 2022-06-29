from typing import TYPE_CHECKING

from aria.core.models import BaseQuerySet

if TYPE_CHECKING:
    from aria.suppliers import models  # noqa


class SupplierQuerySet(BaseQuerySet["models.Supplier"]):
    pass
