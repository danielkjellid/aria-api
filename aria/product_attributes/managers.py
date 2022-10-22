from typing import TYPE_CHECKING

from aria.core.models import BaseQuerySet

if TYPE_CHECKING:
    from aria.product_attributes import models  # noqa


class ColorQuerySet(BaseQuerySet["models.Color"]):
    pass


class ShapeQuerySet(BaseQuerySet["models.Shape"]):
    pass


class SizeQuerySet(BaseQuerySet["models.Size"]):
    pass


class VariantQuerySet(BaseQuerySet["models.Variant"]):
    pass
