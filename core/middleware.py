from django.conf import settings
from django.contrib.sites.models import Site

from urllib.parse import urlparse

class DynamicSiteDomainMiddleware:
    """
    Used to set SITE_ID dynamically, and accordingly based 
    on the site making the request.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        # one time configuration and initialization

    def __call__(self, request):

        host = urlparse(request.META['HTTP_REFERER']).hostname

        try:
            current_site = Site.objects.get(domain=host)
        except Site.DoesNotExist:
            current_site = Site.objects.get(id=settings.DEFAULT_SITE_ID)

        request.current_site = current_site
        settings.SITE_ID = current_site.id

        return self.get_response(request)