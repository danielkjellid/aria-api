from ninja.pagination import paginate, PaginationBase
from ninja import Schema, Field
from typing import Any
from ninja.errors import ConfigError
from ninja.operation import Operation
from ninja.signature.details import is_collection_type
from ninja.types import DictStrAny
from django.db.models import QuerySet
import math
from urllib import parse
from django.utils.encoding import force_str
from aria.api.exceptions import PageOutOfBoundsError


class PaginatedResponseLinks(Schema):
    next: str
    previous: str


class PaginatedResponseMeta(Schema):
    current_page: int
    total: int
    current_range: str
    total_pages: int


class PageNumberSetPagination(PaginationBase):
    def __init__(
        self, page_size: int, order_by: str | None = None, **kwargs: Any
    ) -> None:
        self.page_size = page_size
        self.order_by = (
            order_by if order_by else "id"
        )  # Order by id if no other field is set.
        super().__init__(**kwargs)

    class Input(Schema):
        page: int = Field(1, gt=0)

    class Output(Schema):
        # links: PaginatedResponseLinks
        # meta: PaginatedResponseMeta
        # items: list[Any]
        next: str = None
        previous: str = None
        current_page: int
        total: int
        current_range: str
        total_pages: int
        data: list[Any]

    def paginate_queryset(
        self,
        queryset: QuerySet,
        pagination: Any,
        **params: DictStrAny,
    ) -> Any:
        offset = (pagination.page - 1) * self.page_size
        total_items = self._items_count(queryset)
        total_pages = self._total_pages(total_items)

        if pagination.page > total_pages:
            raise PageOutOfBoundsError()

        qs = queryset.order_by(self.order_by)

        return {
            "next": self._get_next_link(pagination.page, total_pages),
            "previous": self._get_previous_link(pagination.page),
            "current_page": pagination.page,
            "total": total_items,
            "current_range": self._current_range(
                current_offset=offset, total_items=total_items
            ),
            "total_pages": total_pages,
            "data": qs[offset : offset + self.page_size],
        }

    def _current_range(self, current_offset: int, total_items: int):
        """
        Get the current range of instaces being displayed. If page size is
        2, and we're on the first page, it will return 1-2. Will always return
        total_items count istead of end of range if end of range is more than
        total items.
        """

        current_end_of_range = current_offset + self.page_size

        end_of_range = (
            current_end_of_range if current_end_of_range <= total_items else total_items
        )

        return f"{current_offset + 1} - {end_of_range}"

    def _total_pages(self, total_items: int):
        """
        Get the total amount of pages and round up to nearest whole number.
        """
        return math.ceil(total_items / self.page_size)

    def _get_next_link(self, current_page: int, total_pages: int):
        """
        Get url for next page, if the current page is not the last page.
        """
        if current_page == total_pages:
            return None

        url = self.request.build_absolute_uri()
        page_number = current_page + 1
        return self._replace_query_param(url, "page", page_number)

    def _get_previous_link(self, current_page: int):
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
    def _replace_query_param(url: str, key: str, val: str):
        """
        Given a URL and a key/val pair, set or replace an item in the query
        parameters of the URL, and return the new URL.
        """

        scheme, netloc, path, query, fragment = parse.urlsplit(force_str(url))
        query_dict = parse.parse_qs(query, keep_blank_values=True)
        query_dict[force_str(key)] = [force_str(val)]
        query = parse.urlencode(sorted(query_dict.items()), doseq=True)

        return parse.urlunsplit((scheme, netloc, path, query, fragment))
