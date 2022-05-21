from django.contrib.sites.models import Site
from django.conf import settings


def create_site(
    *,
    site_id: int = settings.SITE_ID,
    name: str = "Test site",
    domain: str = "example.com",
) -> Site:

    site, _ = Site.objects.update_or_create(
        id=site_id, defaults={"name": name, "domain": domain}
    )

    return site
