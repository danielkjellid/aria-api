import structlog
from django.db import connection
from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.utils.deprecation import MiddlewareMixin

logger = structlog.get_logger()


class QueryCountWarningMiddleware(MiddlewareMixin):
    """
    Add message in console if number of queries on page load is above threshold.
    Tresholds are set in settings.
    """

    def process_response(
        self, request: HttpRequest, response: HttpResponse
    ) -> HttpResponse:

        if request.path.startswith(settings.STATIC_URL):
            return response

        # Get some debug data from the connection object
        query_count = len(connection.queries)
        query_duration = sum(float(q.get("time")) for q in connection.queries) * 1000

        if settings.DEBUG:
            print(
                "-----------------------------------------------------------------------------------------------------"
            )
            logger.info("query_info", num_queries=query_count, duration=query_duration)
            print(
                "-----------------------------------------------------------------------------------------------------"
            )

        if settings.LOG_SQL:
            for query in connection.queries:
                print(query["sql"])
                print()

        # Check if we've gone above the threshold, and log that's the case
        if (
            query_count > settings.QUERY_COUNT_WARNING_THRESHOLD
            or query_duration > settings.QUERY_DURATION_WARNING_THRESHOLD
        ):
            logger.warning("Query exceeding tresholds!")
            logger.warning(
                "query_warning", num_queries=query_count, duration=query_duration
            )

        return response
