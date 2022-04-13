from urllib.parse import urlparse
from django.conf import settings
from django.contrib.sites.models import Site
from django.db import connection
from django.http import HttpRequest, HttpResponse
from django.utils.deprecation import MiddlewareMixin

import structlog

logger = structlog.get_logger()


class DynamicSiteDomainMiddleware:
    """
    Used to set SITE_ID dynamically, and accordingly based
    on the site making the request.
    """

    def __init__(self, get_response):
        # one time configuration and initialization
        self.get_response = get_response

    def __call__(self, request):

        if request.META.get("HTTP_REFERER") is not None:
            # get hostname from origin making the request
            # if we use djangos built in get_host() it will always return
            # the server ip/hostname
            # which is not what we want when using rest framework
            host = urlparse(request.META.get("HTTP_REFERER")).hostname

            # check if host exists, so we don't hinder request made
            # through the django admin
            if host:
                try:
                    # get the site based on hostname
                    current_site = Site.objects.get(domain=host)
                except Site.DoesNotExist:
                    current_site = Site.objects.get(id=settings.DEFAULT_SITE_ID)

                # set current site and site id to site based on hostname
                request.current_site = current_site
                settings.SITE_ID = current_site.id

                # process request
                return self.get_response(request)
        else:
            return self.get_response(request)


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
