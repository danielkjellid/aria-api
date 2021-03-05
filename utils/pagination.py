from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class PageNumberSetPagination(PageNumberPagination):
    """
    Pagination used for backend tables (overview/list viewpoints)
    """
    
    page_size = 18
    page_size_query_param = 'page_size'
    ordering = 'id'

    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link(),
            },
            'meta': {
                'current_page': int(self.request.query_params.get('page', 1)),
                'total': self.page.paginator.count,
                'current_range': '%s - %s' % (self.page.start_index(), self.page.end_index()),
                'total_pages': self.page.paginator.num_pages,
            },
            'results': data,
        })