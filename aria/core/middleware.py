from typing import Callable

from django.conf import settings
from django.db import connection
from django.http import HttpRequest, HttpResponse
from django.utils.deprecation import MiddlewareMixin

import structlog

logger = structlog.get_logger(__name__)


class QueryCountWarningMiddleware(MiddlewareMixin):
    """
    Add message in console if number of queries on page load is above threshold.
    Thresholds are set in settings.
    """

    @staticmethod
    def process_response(request: HttpRequest, response: HttpResponse) -> HttpResponse:
        """
        Process response by logging query details.
        """
        if request.path.startswith(settings.STATIC_URL):
            return response

        # Get some debug data from the connection object
        query_count = len(connection.queries)
        query_duration = round(
            sum(float(q.get("time")) for q in connection.queries) * 1000  # type: ignore
        )

        if settings.DEBUG:
            logger.info("Query info", num_queries=query_count, duration=query_duration)

        if settings.LOG_SQL:
            for query in connection.queries:
                print(query["sql"])
                print()

        # Check if we've gone above the threshold, and log that's the case
        if (
            query_count > settings.QUERY_COUNT_WARNING_THRESHOLD
            or query_duration > settings.QUERY_DURATION_WARNING_THRESHOLD
        ):
            logger.warning("Query exceeding thresholds!")
            logger.warning(
                "Query warning", num_queries=query_count, duration=query_duration
            )

        return response


class GenericLoggingMiddleware:
    def __init__(self, get_response: Callable[[HttpRequest], None]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> None:
        logger.new(path=request.path, method=request.method)

        if hasattr(request, "user"):
            logger.bind(user_id=request.user.id)

        if hasattr(request, "auth"):
            logger.bind(user_id=request.auth.id)  # type: ignore

        return self.get_response(request)
