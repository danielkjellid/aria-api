from typing import Any, Optional
from urllib import parse

import math
from django.db.models import Model, QuerySet  # pylint: disable=unused-import
from django.utils.encoding import force_str
from django.utils.translation import gettext_lazy as _
from ninja import Field, Schema
from ninja.pagination import PaginationBase
from ninja.types import DictStrAny

from aria.api.exceptions import PageOutOfBoundsError


class PageNumberSetPagination(PaginationBase):
    def __init__(self, page_size: int, **kwargs: Any) -> None:
        self.page_size = page_size
        self.request: Any = None
        super().__init__(**kwargs)

    class Input(Schema):
        page: int = Field(1, gt=0)

    class Output(Schema):
        next: Optional[str] = None
        previous: Optional[str] = None
        current_page: int
        total: int
        current_range: str
        total_pages: int
        data: list[Any]

    def paginate_queryset(
        self,
        queryset: QuerySet["Model"],
        pagination: Any,
        **params: DictStrAny,
    ) -> Any:
        offset = (pagination.page - 1) * self.page_size
        total_items = self._items_count(queryset)
        total_pages = self._total_pages(total_items)

        if pagination.page > total_pages:
            raise PageOutOfBoundsError(_("The page does not exist."))

        return {
            "next": self._get_next_link(pagination.page, total_pages),
            "previous": self._get_previous_link(pagination.page),
            "current_page": pagination.page,
            "total": total_items,
            "current_range": self._current_range(
                current_offset=offset, total_items=total_items
            ),
            "total_pages": total_pages,
            "data": queryset[offset : offset + self.page_size],
        }

    def _current_range(self, current_offset: int, total_items: int) -> str:
        """
        Get the current range of instances being displayed. If page size is
        2, and we're on the first page, it will return 1-2. Will always return
        total_items count instead of end of range if end of range is more than
        total items.
        """

        current_end_of_range = current_offset + self.page_size

        end_of_range = (
            current_end_of_range if current_end_of_range <= total_items else total_items
        )

        return f"{current_offset + 1} - {end_of_range}"

    def _total_pages(self, total_items: int) -> int:
        """
        Get the total amount of pages and round up to the nearest whole number.
        """
        return math.ceil(total_items / self.page_size)

    def _get_next_link(self, current_page: int, total_pages: int) -> Optional[str]:
        """
        Get url for next page, if the current page is not the last page.
        """
        if current_page == total_pages:
            return None

        url = self.request.build_absolute_uri()
        page_number = current_page + 1
        return self._replace_query_param(url, "page", page_number)

    def _get_previous_link(self, current_page: int) -> Optional[str]:
        """
        Get url for the previous page, if the current page is not the first
        page.
        """
        if current_page == 1:
            return None

        url = self.request.build_absolute_uri()
        page_number = current_page - 1
        return self._replace_query_param(url, "page", page_number)

    @staticmethod
    def _replace_query_param(url: str, key: str, val: str | int) -> str:
        """
        Given a URL and a key/val pair, set or replace an item in the query
        parameters of the URL, and return the new URL.
        """

        scheme, netloc, path, query, fragment = parse.urlsplit(force_str(url))
        query_dict = parse.parse_qs(query, keep_blank_values=True)
        query_dict[force_str(key)] = [force_str(val)]
        query = parse.urlencode(sorted(query_dict.items()), doseq=True)

        return parse.urlunsplit((scheme, netloc, path, query, fragment))
