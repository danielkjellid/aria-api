from urllib.parse import urlparse

from django.conf import settings
from django.contrib.sites.models import Site


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
