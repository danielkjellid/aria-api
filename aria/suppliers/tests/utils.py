from django.contrib.sites.models import Site

from aria.core.tests.utils import create_site
from aria.suppliers.models import Supplier


def get_or_create_supplier(
    *,
    supplier_name: str = "Example supplier",
    supplier_discount: float = 0.2,
    origin_country: str = "Norway",
    sites: list[Site] | None = None,
    website_link: str = "example.com",
) -> Supplier:

    supplier, _ = Supplier.objects.get_or_create(
        name=supplier_name,
        contact_first_name="Ola",
        contact_last_name="Nordmann",
        contact_email="ola@example.com",
        supplier_discount=supplier_discount,
        origin_country=origin_country,
        website_link=website_link,
    )

    if sites is None:
        sites = [create_site()]

    supplier.sites.set(sites)

    return supplier
