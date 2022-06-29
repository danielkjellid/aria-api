from django.contrib.sites.models import Site

from aria.core.tests.utils import create_site
from aria.suppliers.models import Supplier


def get_or_create_supplier(
    *,
    supplier_name: str = "Example supplier",
    supplier_discount: float = 0.2,
    origin_country: str = "no",
    sites: list[Site] | None = None,
    website_link: str = "example.com",
) -> Supplier:
    """
    Test utility to create a user instance.
    """
    supplier, _ = Supplier.objects.get_or_create(
        name=supplier_name,
        defaults={
            "contact_first_name": "Ola",
            "contact_last_name": "Nordmann",
            "contact_email": "ola@example.com",
            "supplier_discount": supplier_discount,
            "website_link": website_link,
            "origin_country": origin_country,
        },
    )

    if sites is None:
        sites = [create_site()]

    supplier.sites.set(sites)

    return supplier
