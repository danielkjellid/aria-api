from typing import OrderedDict

from rest_framework.pagination import (
    LimitOffsetPagination as _LimitOffsetPagination,
    PageNumberPagination,
)
from rest_framework.response import Response


class PageNumberSetPagination(PageNumberPagination):
    """
    Pagination used for tables (overview/list viewsets)
    """

    page_size = 18
    page_size_query_param = "page_size"
    ordering = "id"

    def get_paginated_response(self, data):
        return Response(
            {
                "links": {
                    "next": self.get_next_link(),
                    "previous": self.get_previous_link(),
                },
                "meta": {
                    "current_page": int(self.request.query_params.get("page", 1)),
                    "total": self.page.paginator.count,
                    "current_range": "%s - %s"
                    % (self.page.start_index(), self.page.end_index()),
                    "total_pages": self.page.paginator.num_pages,
                },
                "results": data,
            }
        )


def get_paginated_response(
    *, pagination_class, serializer_class, queryset, request, view
):
    """
    The get_paginated_data() method is a helper method for returning a
    paginated response withing an api viewset.
    """

    paginator = pagination_class()

    page = paginator.paginate_queryset(queryset, request, view=view)

    if page is not None:
        serializer = serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    serializer = serializer_class(queryset, many=True)

    return Response(serializer.data)


class LimitOffsetPagination(_LimitOffsetPagination):
    limit = 20  # Override by inheritance
    max_limit = 50

    def get_paginated_data(self, data):
        return OrderedDict(
            [
                ("limit", self.limit),
                ("offset", self.offset),
                ("count", self.count),
                ("next", self.get_next_link()),
                ("previous", self.get_previous_link()),
                ("data", data),
            ]
        )

    def get_paginated_response(self, data):
        """
        We redefine this method in order to return `limit` and `offset`.
        This is used by the frontend to construct the pagination itself.
        """

        return Response(
            OrderedDict(
                [
                    ("limit", self.limit),
                    ("offset", self.offset),
                    ("count", self.count),
                    ("next", self.get_next_link()),
                    ("previous", self.get_previous_link()),
                    ("results", data),
                ]
            )
        )
