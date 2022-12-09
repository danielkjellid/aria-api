from typing import TypeVar

from django.db import models
from django.db.models import Case, When

T = TypeVar("T", bound=models.Model)


class BaseQuerySet(models.QuerySet[T]):
    def order_by_ids(self, ids: list[int]) -> models.QuerySet[T]:
        """
        Order queryset by a fixed list of ids.
        """
        if not ids:
            return self

        preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(ids)])
        return self.order_by(preserved)
